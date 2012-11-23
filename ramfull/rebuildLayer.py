
import pyglet
import random

from pyglet_piss import Actions
from gamePhaseLayer import GamePhaseLayer
from firePhase import FirePhase

from tile import Tile
from tileObject import Wall
from sounds import AllSounds

class Piece(object):
    WIDTH = 3
    HEIGHT = 3
    
    rotations = [
            [ 0, 1, 2, 3, 4, 5, 6, 7, 8 ],
            [ 2, 5, 8, 1, 4, 7, 0, 3, 6 ],
            [ 8, 7, 6, 5, 4, 3, 2, 1, 0 ],
            [ 6, 3, 0, 7, 4, 1, 8, 5, 2 ],
            ]
    
    def __init__(self, a):
        self.walls = a
        self.neighbors = [ self._getNeighbors(i) for i in range(len(a)) ]
        
    
    def getRotated(self, i):
        """Returns a tuple: (walls, neighbors) for the ith rotation of this
        piece.
        """
        return (
                self._rotateArray(self.walls, i),
                self._rotateArray(self.neighbors, i)
        )
        
        
    def _getNeighbors(self, i):
        """Return neighbors array (suitable for Wall.getImage) for the
        given index."""
        x = i % self.WIDTH
        y = int(i / self.WIDTH)
        return [ self._checkSpot(x, y - 1), self._checkSpot(x + 1, y),
                self._checkSpot(x, y + 1), self._checkSpot(x - 1, y) ]
        
        
    def _checkSpot(self, x, y):
        if x < 0 or y < 0 or x >= self.WIDTH or y >= self.HEIGHT:
            return False
        i = y * self.WIDTH + x
        if self.walls[i]:
            return True
        return False
    
    
    def _rotateArray(self, arr, i):
        return [ arr[j] for j in self.rotations[i] ]
        

pieces = [
        # Each piece is a 3x3 grid centered around 1,1...
        [ 0, 0, 0, 0, 1, 0, 0, 0, 0 ],
        [ 0, 0, 0, 1, 1, 1, 0, 0, 0 ],
        [ 0, 1, 0, 1, 1, 0, 0, 0, 0 ],
        [ 0, 1, 0, 1, 1, 1, 0, 0, 0 ],
        [ 0, 1, 1, 0, 1, 1, 0, 0, 0 ],
        ]
pieces = [ Piece(p) for p in pieces ]
        

class RebuildLayer(GamePhaseLayer):
    
    TICKER = "REBUILD"
    TIMER = 20.0
    
    def _layerInit(self, scene):
        super(RebuildLayer, self)._layerInit(scene)
        
        self.s = pyglet.sprite.Sprite(Wall.DEFAULT_IMAGE)
        
        self.scene.board.territoryCheck()
        
        self.playerMap = {}
        for p in scene.app.players:
            if not p.inGame:
                continue
            self.playerMap[p] = { 'piece': self._nextPiece(), 'rotate': 0 }
            # Move each player back to their castle
            p.inGame.x = p.inGame.homeX
            p.inGame.y = p.inGame.homeY
            
        # Wait for update to let players place tiles 
        self.hasUpdated = False
    
    
    def drawPlayer(self, p, x, y):
        if self.playerMap[p]['piece'] is not None:
            walls, neighbors = self._getPlayerPiece(p)
            color = (255, 200, 200)
            if self._canPlace(p, walls):
                color = (255, 255, 255)
            self.s.color = color
            
            for ix in [-1, 0, 1]:
                for iy in [-1, 0, 1]:
                    i = (iy + 1) * Piece.WIDTH + (ix + 1)
                    if not walls[i]:
                        continue
                    self.s.image = Wall.getImage(neighbors[i])
                    self.s.x = x + ix * Tile.SIZE
                    self.s.y = y + iy * Tile.SIZE
                    self.s.draw()    
            
        self.drawCursor(p, x, y)
        
        
    def onAction(self, player, action):
        if not player.inGame:
            return super(RebuildLayer, self).onAction(player, action)
        
        if action == Actions.BTN1:
            if not self.hasUpdated:
                return super(RebuildLayer, self).onAction(player, action)
            if self.playerMap[player]['piece'] is not None:
                walls, _ = self._getPlayerPiece(player)
                if self._canPlace(player, walls):
                    self._doPlace(player, walls)
        elif action == Actions.BTN2:
            pm = self.playerMap[player]
            pm['rotate'] = (pm['rotate'] + 1) % len(Piece.rotations)
        else:
            return super(RebuildLayer, self).onAction(player, action)
        return True
        
    
    def onTimer(self):
        # Do nothing, wait for all players to finish
        self.secondTimer = 5.0
    
    
    def onUpdate(self, dt):
        self.hasUpdated = True
        super(RebuildLayer, self).onUpdate(dt)
        if self.timer is None:
            self.secondTimer -= dt
            isDone = True
            for p in self.playerMap.values():
                if p['piece'] is not None:
                    isDone = False
            if isDone or self.secondTimer < 0.0:
                self.remove()
                from scorePhase import ScorePhase
                self.scene.addLayer(ScorePhase()) 
        
        
    def _canPlace(self, player, walls):
        px = player.inGame.x
        py = player.inGame.y
        for ix in [-1, 0, 1]:
            for iy in [-1, 0, 1]:
                i = (iy + 1) * Piece.WIDTH + (ix + 1)
                if not walls[i]:
                    continue
                t = self.scene.board.get(px + ix, py + iy)
                if t is None:
                    return False
                if t.owner != player:
                    return False
                if t.object is not None:
                    return False
        return True
    
    
    def _doPlace(self, player, walls):
        px = player.inGame.x
        py = player.inGame.y
        for ix in [-1, 0, 1]:
            for iy in [-1, 0, 1]:
                i = (iy + 1) * Piece.WIDTH + (ix + 1)
                if not walls[i]:
                    continue
                w = Wall(px + ix, py + iy)
                self.scene.board.addObj(w)
                
        # Re-check territory...  Essentially, we have to re-check all neighbors
        # that aren't currently territory or a wall.
        board = self.scene.board
        toCheck = []
        for ix in range(-2, 3):
            for iy in range(-2, 3):
                toCheck.append((px + ix, py + iy))
        if board.territoryCheck(toCheck):
            AllSounds.NEW_TERRITORY.play(minTime = 0.7)
        else:
            AllSounds.WALL.play(minTime = 0.3, maxInstances = 3)
                
        pm = self.playerMap[player]
        pm['rotate'] = 0
        pm['piece'] = self._nextPiece()
        
        
    def _getPlayerPiece(self, player):
        pm = self.playerMap[player]
        return pm['piece'].getRotated(pm['rotate'])
        
        
    def _nextPiece(self):
        if self.timer is None:
            return None
        return random.choice(pieces)
    
    