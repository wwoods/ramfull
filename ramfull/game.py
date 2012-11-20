
import pyglet
from pyglet_piss import Scene

from ramfull.board import Board
from ramfull.godLayer import GodLayer
from ramfull.placeLayer import PlaceLayer
from ramfull.player import RamfullPlayer
from ramfull.tile import Tile

class GameScene(Scene):
    
    showFps = True
    
    def __init__(self):
        Scene.__init__(self)
        
        
    def _sceneInit(self, app):
        Scene._sceneInit(self, app)
        
        bw = int(self.window.width / Tile.SIZE)
        bh = int(self.window.height / Tile.SIZE)
        self.board = Board(bw, bh, self.app.players)
        
        for p in self.app.players:
            p.inGame = RamfullPlayer()
        
        self.addLayer(PlaceLayer())
    
    
    def onDraw(self):
        self.window.clear()
        self.board.draw()
    
        