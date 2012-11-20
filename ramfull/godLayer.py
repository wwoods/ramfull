
import pyglet
from pyglet_piss import Actions

from ramfull.tile import Tile, TileTypes
from ramfull.images import PlayerImages

from ramfull.playerLayer import PlayerLayer

class GodLayer(PlayerLayer):
    def onAction(self, player, action):
        if not player.inGame:
            return
        
        if action == Actions.BTN1:
            x = player.inGame.x
            y = player.inGame.y
            t = self.board.get(x, y)
            t.setType((t.type + 1) % TileTypes.MAX)
        else:
            return PlayerLayer.onAction(player, action)
        return True
    
    
    def drawPlayer(self, p, x, y):
        self.drawCursor(p, x, y)
        