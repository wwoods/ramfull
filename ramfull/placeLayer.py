
import pyglet
from pyglet_piss import Actions
from ramfull.playerLayer import PlayerLayer
from ramfull.images import TileObjectImages
from ramfull.tile import Tile
from ramfull.tileObject import Castle, Cannon

class PlaceLayer(PlayerLayer):
    
    def _layerInit(self, scene):
        PlayerLayer._layerInit(self, scene)
        self.placer = pyglet.sprite.Sprite(TileObjectImages.UNKNOWN)
        self.placeInfo = {}
        for p in self.scene.app.players:
            if p.inGame:
                self.placeInfo[p] = Cannon


    def drawPlayer(self, p, x, y):
        pi = self.placeInfo[p]
        self.placer.image = pi.DEFAULT_IMAGE
        tw = int(pi.DEFAULT_IMAGE.width / Tile.SIZE)
        th = int(pi.DEFAULT_IMAGE.height / Tile.SIZE)
        self.placer.x = x
        self.placer.y = y
        if self.board.canPlace(p.inGame.x, p.inGame.y, tw, th):
            self.placer.color = (255, 255, 255)
        else:
            self.placer.color = (255, 200, 200)
        self.placer.draw()
        
        self.drawCursorLarge(p, x, y, tw, th)
                
                
    def onAction(self, player, action):
        if not player.inGame:
            return False
        
        if action == Actions.BTN1:
            pi = self.placeInfo[player]
            x = player.inGame.x
            y = player.inGame.y
            if self.board.canPlace(x, y, pi.tilesWide, pi.tilesHigh):
                c = pi(x, y)
                self.board.addObj(c)
        else:
            return PlayerLayer.onAction(self, player, action)
        return True
        
        