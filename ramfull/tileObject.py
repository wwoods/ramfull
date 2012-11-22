
import pyglet
from images import TileObjectImages

from tile import Tile

class TileObject(object):
    DEFAULT_IMAGE = TileObjectImages.UNKNOWN
    HEALTH = 1
    
    @property
    def tilesHigh(self):
        return int(self.DEFAULT_IMAGE.height / Tile.SIZE)
    
    @property
    def tilesWide(self):
        return int(self.DEFAULT_IMAGE.width / Tile.SIZE)
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = self.HEALTH
        self.isRemoved = False
        
        
    def hit(self):
        """We were hit by a cannonball!!!"""
        if self.health is not None:
            self.health -= 1
            if self.health <= 0:
                self.scorchAndRemove()
        
        
    def remove(self):
        self.sprite.delete()
        self.board.removeObj(self)
        self.isRemoved = True
        
        
    def _tileObjectInit(self, board):
        self.board = board
        self.sprite = pyglet.sprite.Sprite(self.DEFAULT_IMAGE,
                batch = board.tileObjsBatch)
        
        
    def preDraw(self):
        """Determine which image our sprite should be using"""
        self.sprite.x = self.x * Tile.SIZE
        self.sprite.y = self.y * Tile.SIZE
        
        
    def scorchAndRemove(self):
        """Scorch all tiles under this object, and remove the object.
        """
        for ix in range(0, self.tilesWide):
            for iy in range(0, self.tilesHigh):
                t = self.board.get(self.x + ix, self.y + iy)
                t.scorch()
        self.remove()
        
        
class Wall(TileObject):
    DEFAULT_IMAGE = TileObjectImages.WALL_ALONE
    
    @classmethod
    def getImage(cls, neighbors):
        # Neighbors is array: [ isWallToNorth, isWallToEast, isWallToSouth,
        #    isWallToWest ]
        i = {
             ( False, False, False, False ): TileObjectImages.WALL_ALONE,
             ( True, False, False, False): TileObjectImages.WALL_VERT,
             ( False, True, False, False): TileObjectImages.WALL_HORZ,
             ( True, True, False, False): TileObjectImages.WALL_NE,
             ( False, False, True, False): TileObjectImages.WALL_VERT,
             ( True, False, True, False): TileObjectImages.WALL_VERT,
             ( False, True, True, False): TileObjectImages.WALL_SE,
             ( True, True, True, False): TileObjectImages.WALL_E,
             ( False, False, False, True): TileObjectImages.WALL_HORZ,
             ( True, False, False, True): TileObjectImages.WALL_NW,
             ( False, True, False, True): TileObjectImages.WALL_HORZ,
             ( True, True, False, True): TileObjectImages.WALL_N,
             ( False, False, True, True): TileObjectImages.WALL_SW,
             ( True, False, True, True): TileObjectImages.WALL_W,
             ( False, True, True, True): TileObjectImages.WALL_S,
             ( True, True, True, True): TileObjectImages.WALL_ALL,
             }[tuple(neighbors)]
        if i == TileObjectImages.UNKNOWN:
            # Filler code till graphics
            i = TileObjectImages.WALL_ALONE
        return i
    
    
    def getNeighbors(self):
        m = (self._checkNeighbor(0, 1), self._checkNeighbor(1, 0),
                self._checkNeighbor(0, -1), self._checkNeighbor(-1, 0))
        return m
            
            
    def preDraw(self):
        TileObject.preDraw(self)
        self.sprite.image = self.getImage(self.getNeighbors())
        
        
    def _checkNeighbor(self, xd, yd):
        t = self.board.get(self.x + xd, self.y + yd)
        if t is None:
            return False
        if isinstance(t.object, Wall):
            return True
        return False
    
    
class Castle(TileObject):
    tilesWide = 2
    tilesHigh = 2
    
    DEFAULT_IMAGE = TileObjectImages.CASTLE
    HEALTH = None
    
    def __init__(self, x, y, minX, maxX, minY, maxY):
        """Min / Max X and Y specify grounds including outer wall
        """
        TileObject.__init__(self, x, y)
        self._grounds = []
        self._walls = []
        for x in range(minX + 1, maxX):
            for y in range(minY + 1, maxY):
                self._grounds.append((x, y))
                
        for x in range(minX, maxX + 1):
            self._walls.append((x, minY))
            self._walls.append((x, maxY))
        for y in range(minY + 1, maxY):
            self._walls.append((minX, y))
            self._walls.append((maxX, y))
            
            
    def groundsAdd(self):
        for x,y in self._grounds:
            t = self.board.get(x, y)
            t.isTerritory = True
            t.update()
        for x,y in self._walls:
            w = Wall(x, y)
            self.board.addObj(w)
            
            
    def groundsRemove(self):
        for x, y in self._grounds:
            t = self.board.get(x, y)
            t.isTerritory = False
            t.update()
            
        for x, y in self._walls:
            t = self.board.get(x, y)
            t.object.remove()
    
    
class PlaceableTileObject(TileObject):
    cannonCount = 1
    
    @classmethod
    def canPlace(cls, player, board, x, y):
        return board.canPlace(x, y, cls.tilesWide, cls.tilesHigh,
                territoryOwner = player)


class Cannon(PlaceableTileObject):
    tilesWide = 2
    tilesHigh = 2
    
    DEFAULT_IMAGE = TileObjectImages.CANNON
    HEALTH = 8
    