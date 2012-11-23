
import pyglet
import random

from ramfull.tile import TileImages, Tile, TileTypes
from ramfull.tileObject import Castle, Wall
        

class Board(object):
    """A ramfull board"""
    
    def __init__(self, width, height, players):
        self.width = width
        self.height = height
        
        self.tiles = []
        self.batch = pyglet.graphics.Batch()
        for y in range(height):
            for x in range(width):
                self.tiles.append(Tile(self, x, y, self.batch))
        # Fill out "neighbors"
        for y in range(height):
            for x in range(width):
                t = self.get(x, y)
                t.neighbors = [ self.get(x, y + 1), self.get(x + 1, y),
                               self.get(x, y - 1), self.get(x - 1, y) ]
                
        # Tile objects
        self.tileObjs = []
        self.tileObjsBatch = pyglet.graphics.Batch()
        
        # Generate the map!
        self._generate(players)
        
        
    def addObj(self, object):
        """Unconditionally add object to tileObjs"""
        self.tileObjs.append(object)
        object._tileObjectInit(self)
        for tx in range(object.x, object.x + object.tilesWide):
            for ty in range(object.y, object.y + object.tilesHigh):
                t = self.get(tx, ty)
                if t is not None:
                    t.object = object 
        
        
    def canPlace(self, x, y, w, h, territoryOwner = None):
        for ix in range(x, x + w):
            for iy in range(y, y + h):
                t = self.get(ix, iy)
                if t is None:
                    return False
                if t.object is not None:
                    return False
                if t.type != TileTypes.GRASS:
                    return False
                if territoryOwner is not None and (
                        not t.isTerritory or t.owner != territoryOwner):
                    return False
        return True
                
                
    def draw(self):
        for t in self.tileObjs:
            t.preDraw()
        self.batch.draw()
        self.tileObjsBatch.draw()
        
        
    def get(self, x, y):
        """Return the tile at (x,y)"""
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None
        return self.tiles[y * self.width + x]
    
    
    def removeObj(self, obj):
        self.tileObjs.remove(obj)
        for tx in range(obj.x, obj.x + obj.tilesWide):
            for ty in range(obj.y, obj.y + obj.tilesHigh):
                t = self.get(tx, ty)
                if t is not None:
                    t.object = None
                    
                    
    def territoryCheck(self, tilesToCheck = None):
        """Using tilesToCheck as starting points, see if any of them are 
        contained in new territory.
        
        tilesToCheck is an array of (x, y) coords
        
        If tilesToCheck is None, wipe all territory and do the whole board.
        
        Returns True if anything resulted in new territory; false otherwise.
        """
        
        if tilesToCheck is None:
            tilesToCheck = []
            for t in self.tiles:
                t.isTerritory = False
                t.update()
                tilesToCheck.append((t.x, t.y))
                
        newTerritory = False
        tilesChecked = set()
        for x, y in tilesToCheck:
            coords = (x,y)
            baseTile = self.get(x, y)
            if baseTile is None:
                continue
            
            player = baseTile.owner
            tilesToCheck = [ coords ]
            tilesInTurf = set()
            
            noGood = False
            
            while len(tilesToCheck) > 0:
                # Pop off top so that we travel in a straight line as long
                # as we can.
                coords = tilesToCheck.pop()
                x, y = coords
                i = y * self.width + x
                if i in tilesInTurf:
                    # This tile already processed
                    continue
                if i in tilesChecked:
                    # Territory / not has already been decided for this
                    # whole chunk; throw it out
                    noGood = True
                    break
                
                t = self.get(x, y)
                if t is None or t.owner != player:
                    # Whole chunk is invalid, we reached the border of 
                    # player territory
                    noGood = True
                    break
                
                if isinstance(t.object, Wall):
                    # It's walled, therefore a boundary.  Skip it
                    continue
                
                # It's new to the turf and a valid part, add it
                tilesInTurf.add(i)
                
                # At this point, it's valid turf, push our neighbors -
                # including diagonals
                tilesToCheck.append((x, y + 1))
                tilesToCheck.append((x + 1, y))
                tilesToCheck.append((x, y - 1))
                tilesToCheck.append((x - 1, y))
                tilesToCheck.append((x + 1, y + 1))
                tilesToCheck.append((x + 1, y - 1))
                tilesToCheck.append((x - 1, y - 1))
                tilesToCheck.append((x - 1, y + 1))
                
            if not noGood:
                for i in tilesInTurf:
                    x = i % self.width
                    y = int(i / self.width)
                    t = self.get(x, y)
                    if not t.isTerritory:
                        newTerritory = True
                        t.isTerritory = True
                        t.update()
            
            # Make sure no future passes check this tile
            tilesChecked.update(tilesInTurf)
            
        return newTerritory

    
    def _generate(self, players):
        # Expand each player's territory by 1 tile at a time, until they hit
        # each other.  Make a river there.
        
        # Index clockwise from lower-left, non-inclusive
        borderMax = 2 * self.width + 2 * self.height
        numPlayers = max(2, len(players))
        pInterval = int(borderMax / numPlayers)
        
        playerTurfs = {}
        playerStarts = {}
        playerLast = int(random.random() * pInterval)
        for p in range(numPlayers):
            playerStart = (playerLast + pInterval) % borderMax
            print("Looking at {0} of {1} from {2}".format(playerStart, 
                    borderMax, playerLast))
            playerLast = playerStart
            if playerStart < self.height:
                x = 0
                y = playerStart
            elif playerStart < self.height + self.width:
                y = self.height - 1
                x = playerStart - self.height
            elif playerStart < self.height * 2 + self.width:
                x = self.width - 1
                y = self.height - 1 - (playerStart - self.height - self.width)
            else:
                y = 0
                x = self.width - 1 - (
                        playerStart - self.height * 2 - self.width)
            print("Starting: {0},{1} ({2})".format(x, y, pInterval))
            playerTurfs[p] = [ (x,y,0) ]
            playerStarts[p] = (x,y)
            
        def insort_right(spots, x, y, start, lo=0, hi=None):
            """Ripped from bisect"""
            dist = (x - start[0]) ** 2 + (y - start[1]) ** 2
            dist *= 0.9 + 0.2 * random.random()
            if hi is None:
                hi = len(spots)
            while lo < hi:
                mid = (lo+hi) // 2
                if dist < spots[mid][2]: hi = mid
                else: lo = mid+1
            spots.insert(lo, (x, y, dist))
            
        def tryConvert(p, spots, x, y):
            t = self.get(x, y)
            if t is None or t.type == TileTypes.SEA:
                return False
            
            if t.owner is not None and t.owner != p:
                t.setType(TileTypes.SEA)
                t.owner = None
                return False
            
            if t.owner is not None:
                return False
            
            t.owner = p
            ps = playerStarts[p]
            insort_right(spots, x + 1, y, ps)
            insort_right(spots, x, y + 1, ps)
            insort_right(spots, x - 1, y, ps)
            insort_right(spots, x, y - 1, ps)
            return True
        
        while True:
            hadElement = False
            for p, spots in playerTurfs.iteritems():
                while len(spots) > 0:
                    q = spots.pop(0)
                    if tryConvert(p, spots, q[0], q[1]):
                        hadElement = True
                        break
            if not hadElement:
                break
            
        # Now convert all tile owners to player references
        for t in self.tiles:
            if t.owner is not None:
                if t.owner < len(players):
                    t.owner = players[t.owner]
                else:
                    t.owner = None
                    
        # Update graphics
        for t in self.tiles:
            t.update()
                    
        # Sprinkle castles...  castles need room for at least one cannon
        # between the wall and the castle, and then a surrounding wall and
        # a one-tile barrier.
        minCastleSide = 4
        def canCastle(x, y):
            minX = x - minCastleSide
            maxX = x + 1 + minCastleSide
            minY = y - minCastleSide
            maxY = y + 1 + minCastleSide
            isOk = True
            for cx in range(minX, maxX + 1):
                for cy in range(minY, maxY + 1):
                    t = self.get(cx, cy)
                    if t is None:
                        isOk = False
                        break
                    elif t.type != TileTypes.GRASS:
                        isOk = False
                        break
                    elif t.object is not None:
                        isOk = False
                        break
                    elif t.gen_castleGrounds is not None:
                        isOk = False
                        break
                    
            if isOk:
                castle = Castle(x, y, minX + 1, maxX - 1, minY + 1, maxY - 1)
                self.addObj(castle)
                for cx in range(minX, maxX + 1):
                    for cy in range(minY, maxY + 1):
                        self.get(cx, cy).gen_castleGrounds = castle
                        
        tilesToCheck = []
        for x in range(self.width):
            for y in range(self.height):
                tilesToCheck.append((x, y))
        random.shuffle(tilesToCheck)
        for (x, y) in tilesToCheck:
            canCastle(x, y)
        
        