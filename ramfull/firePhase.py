
import math

import pyglet
from pyglet_piss import Actions
from ramfull.gamePhaseLayer import GamePhaseLayer
from images import TileObjectImages
from sounds import AllSounds
from tile import Tile
from tileObject import Cannon

class CannonBall(pyglet.sprite.Sprite):
    def __init__(self, batch, cannon, x, y):
        super(CannonBall, self).__init__(TileObjectImages.CANNONBALL,
                batch = batch)
        self.cannon = cannon
        self.targetX = x
        self.targetY = y
        dist = (x - cannon.x) ** 2 + (y - cannon.y) ** 2
        dist = math.sqrt(dist)
        self.time = dist / 10.0
        self.dist = dist
        self.maxTime = self.time
        AllSounds.CANNON.play(minTime = 0.4, maxInstances = 6)
        
        
    def update(self, dt):
        self.time -= dt
        if self.time < 0:
            # DONE!  Remove from batch and tell PhaseData to remove us
            self.delete()
            AllSounds.HIT.play(minTime = 0.3, maxInstances = 4, volume = 0.1)
            return True
        
        baseX = (self.cannon.x + self.cannon.tilesWide * 0.5) * Tile.SIZE
        baseY = (self.cannon.y + self.cannon.tilesHigh * 0.5) * Tile.SIZE
        targX = (self.targetX + 0.5) * Tile.SIZE
        targY = (self.targetY + 0.5) * Tile.SIZE
        
        bi = self.time / self.maxTime
        ti = 1.0 - bi
        z = 1.0 - (2 * abs(0.5 - bi)) ** 2
        self.scale = 1.0 + z
        sw = self.image.width * self.scale
        sh = self.image.height * self.scale
        self.x = baseX * bi + targX * ti - sw * 0.5
        yoff = z * (10 + 10 * self.dist ** 0.5)
        self.y = baseY * bi + targY * ti + yoff - sh * 0.5


class FirePhaseData(object):
    def __init__(self, board):
        self.cannons = []
        self.cannonBalls = {}
        self.board = board
        self.batch = pyglet.graphics.Batch()
        
        
    def draw(self):
        self.batch.draw()
        
        
    def isDone(self):
        if len(self.cannonBalls) == 0:
            return True
        return False
        
        
    def tryFire(self, x, y):
        self._cleanCannons()
        cannon = None
        for c in self.cannons:
            if c not in self.cannonBalls:
                cannon = c
                break
        if cannon is None:
            return
        self.cannonBalls[cannon] = CannonBall(self.batch, cannon, x, y)
        
        
    def update(self, dt):
        for cannon, ball in self.cannonBalls.items():
            if not ball.update(dt):
                continue
            del self.cannonBalls[cannon]
            t = self.board.get(ball.targetX, ball.targetY)
            if t.object is not None:
                t.object.hit()
            else:
                t.scorch()
                
                
    def _cleanCannons(self):
        for c in self.cannons[:]:
            if c.isRemoved:
                self.cannons.remove(c)
            
        

class FirePhase(GamePhaseLayer):
    TICKER = 'READY, AIM...'
    TIMER = 24.0
    
    def _layerInit(self, scene):
        self.scene = scene
        
        hadCannons = False
        self.playerMap = {}
        for p in self.scene.app.players:
            if not p.inGame:
                continue
            self.playerMap[p] = FirePhaseData(self.scene.board)
            
        # Make sure anyone CAN fire.  Also, restore the health of all TileObjs.
        for t in self.scene.board.tileObjs:
            t.health = t.HEALTH
            if not isinstance(t, Cannon):
                continue
            
            tile = self.scene.board.get(t.x, t.y)
            if tile.isTerritory:
                self.playerMap[tile.owner].cannons.append(t)
                hadCannons = True
                
        if not hadCannons:
            # Skip this phase, go straight to rebuilding - no one had cannons!
            self.remove()
            # Avoid circular dependency here
            from rebuildLayer import RebuildLayer
            self.scene.addLayer(RebuildLayer())
            return
                
        self.hasUpdated = False # Wait for ticker to clear before firing
        GamePhaseLayer._layerInit(self, scene)
        
    
    def drawPlayer(self, p, x, y):
        self.drawCursor(p, x, y)
        
        
    def onAction(self, player, action):
        if not player.inGame or not self.hasUpdated:
            return super(FirePhase, self).onAction(player, action)
        
        if self.timer is None:
            # Timer clicked, don't do anything
            return super(FirePhase, self).onAction(player, action)
        
        fpd = self.playerMap[player]
        if action == Actions.BTN1 or action == Actions.BTN2:
            fpd.tryFire(player.inGame.x, player.inGame.y)
        else:
            return super(FirePhase, self).onAction(player, action)
        
        return True
    
    
    def onDraw(self):
        super(FirePhase, self).onDraw()
        
        for fpd in self.playerMap.values():
            fpd.draw()
        
        
    def onTimer(self):
        pass # Wait for cannon balls to flow
        
        
    def onUpdate(self, dt):
        self.hasUpdated = True
        super(FirePhase, self).onUpdate(dt)
        isDone = True
        for fpd in self.playerMap.values():
            fpd.update(dt)
            if not fpd.isDone():
                isDone = False
        if isDone and self.timer is None:
            # Avoid circular dependency here
            from rebuildLayer import RebuildLayer
            self.remove()
            self.scene.addLayer(RebuildLayer())
    