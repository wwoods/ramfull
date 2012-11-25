
import pyglet
from pyglet_piss import Scene

from ramfull.board import Board
from ramfull.godLayer import GodLayer
from ramfull.selectCastle import SelectCastleLayer
from ramfull.tile import Tile
from images import PlayerImages

class GameScene(Scene):
    
    showFps = True
        
        
    def _sceneInit(self, app):
        Scene._sceneInit(self, app)
        
        # Unset by ScorePhase.
        self.isFirstRound = True
        
        for p in self.app.players:
            p.inGame = None
            p.name = PlayerImages.names[p.id]
        
        self.remakeBoard()
        
        #self.addLayer(SelectCastleLayer())
        from optInLayer import OptInLayer
        self.addLayer(OptInLayer())
    
    
    def onDraw(self):
        self.window.clear()
        self.board.draw()
        
        
    def remakeBoard(self):
        bw = int(self.window.width / Tile.SIZE)
        bh = int(self.window.height / Tile.SIZE)
        players = []
        for p in self.app.players:
            if p.inGame:
                players.append(p)
        self.board = Board(bw, bh, players)
    
