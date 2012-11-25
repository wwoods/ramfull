
import math

import pyglet
from pyglet_piss import Actions
from ramfull.firePhase import FirePhase
from ramfull.images import TileObjectImages
from ramfull.gamePhaseLayer import GamePhaseLayer
from sounds import AllSounds
from ramfull.tile import Tile
from ramfull.tileObject import Castle, Cannon

class PlaceCannonInfo(object):
    def __init__(self, p, numCannons):
        self.p = p
        self.numCannons = numCannons
        self.obj = Cannon
        

class PlaceLayer(GamePhaseLayer):
    
    TICKER = 'PLACE CANNONS'
    TIMER = 10.0
    
    def _layerInit(self, scene):
        self.scene = scene
        
        # Players might build over there territory, so remove that so as not
        # to confuse whether or not a player can place any cannons
        self.scene.board.territoryCheck()
        
        baseCannons = 1
        if self.scene.isFirstRound:
            # Extra cannon for round one
            baseCannons = 2
        
        castlesPerPlayer = {}
        for p in self.scene.app.players:
            castlesPerPlayer[p] = 0
            
        for to in self.scene.board.tileObjs:
            if not isinstance(to, Castle):
                continue
            t = self.scene.board.get(to.x, to.y)
            if t.isTerritory:
                castlesPerPlayer[t.owner] += 1
         
        hadCannons = False
        self.placer = pyglet.sprite.Sprite(TileObjectImages.UNKNOWN)
        self.label = pyglet.text.Label(anchor_x = 'center', anchor_y = 'center')
        self.label.bold = True
        self.placeInfo = {}
        for p in self.scene.app.players:
            if p.inGame:
                self.placeInfo[p] = PlaceCannonInfo(p,
                        baseCannons + castlesPerPlayer[p])
                if not self._checkPlayerSpace(p):
                    self.placeInfo[p].numCannons = 0
                else:
                    hadCannons = True
        
        # No cannons to place?  Skip this phase
        if not hadCannons:
            self.remove()
            self.scene.addLayer(FirePhase())
            return
         
        GamePhaseLayer._layerInit(self, scene)       
        


    def drawPlayer(self, p, x, y):
        pi = self.placeInfo[p]
        obj = pi.obj
        if pi.numCannons > 0:
            self.placer.image = pi.obj.DEFAULT_IMAGE
            tw = int(pi.obj.DEFAULT_IMAGE.width / Tile.SIZE)
            th = int(pi.obj.DEFAULT_IMAGE.height / Tile.SIZE)
            self.placer.x = x
            self.placer.y = y
            if (pi.numCannons >= obj.cannonCount
                    and obj.canPlace(p, self.board, p.inGame.x, p.inGame.y)):
                self.placer.color = (255, 255, 255)
            else:
                self.placer.color = (255, 200, 200)
            self.placer.draw()
            
            # Draw # remaining
            self.label.x = x + tw * Tile.SIZE * 0.5
            self.label.y = y + th * Tile.SIZE * 0.5
            self.label.text = str(int(pi.numCannons / obj.cannonCount))
            self.label.draw()
            
            self.drawCursorLarge(p, x, y, tw, th)
        else:
            # Done, draw normal cursor
            self.drawCursor(p, x, y)


    def onAction(self, player, action):
        if not player.inGame:
            return False
        
        if action == Actions.BTN1:
            pi = self.placeInfo[player]
            obj = pi.obj
            if pi.numCannons >= obj.cannonCount:
                x = player.inGame.x
                y = player.inGame.y
                if obj.canPlace(player, self.board, x, y):
                    c = obj(x, y)
                    self.board.addObj(c)
                    AllSounds.WALL.play(minTime = 0.3, maxInstances = 3)
                    pi.numCannons -= obj.cannonCount
                    if pi.numCannons > 0 and not self._checkPlayerSpace(player):
                        pi.numCannons = 0
        else:
            return GamePhaseLayer.onAction(self, player, action)
        return True
    
    
    def onTimer(self):
        self.remove()
        self.scene.addLayer(FirePhase())
    
    
    def onUpdate(self, dt):
        super(PlaceLayer, self).onUpdate(dt)
        allPlayersDone = True
        for p in self.scene.app.players:
            if not p.inGame:
                continue
            if self.placeInfo[p].numCannons != 0:
                allPlayersDone = False
                break
        if allPlayersDone:
            self.onTimer()
            
            
    def _checkPlayerSpace(self, player):
        """Return False if player does not have room for a 2x2 cannon.
        """
        board = self.scene.board
        for t in board.tiles:
            if t.owner != player:
                continue
            if not t.isTerritory:
                continue
            if t.object is not None:
                continue
            isOk = True
            for x,y in [ (1, 0), (0, 1), (1, 1) ]:
                t2 = board.get(t.x + x, t.y + y)
                if (t2.owner != player
                        or not t2.isTerritory
                        or t2.object is not None):
                    isOk = False
                    break
            if isOk:
                # Space for a cannon!
                return True
        return False
        