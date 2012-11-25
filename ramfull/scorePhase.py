
import pyglet
from pyglet_piss import Actions
from gamePhaseLayer import GamePhaseLayer

from tileObject import Castle
from images import PlayerImages

class ScorePhase(GamePhaseLayer):
    TICKER = None
    TIMER = 2
    
    def _layerInit(self, scene):
        super(ScorePhase, self)._layerInit(scene)
        
        # No longer first round!
        scene.isFirstRound = False
        
        self.text = pyglet.text.HTMLLabel(anchor_x = 'center', 
                anchor_y = 'center', width = self.window.width, 
                multiline = True)
        self.text.x = self.window.width * 0.5
        self.text.y = self.window.height * 0.5
        
        castleCounts = {}
        for p in self.scene.app.players:
            if not p.inGame:
                continue
            castleCounts[p] = 0
            
        board = self.scene.board
        for c in board.tileObjs:
            if not isinstance(c, Castle):
                continue
            t = board.get(c.x, c.y)
            if t.isTerritory:
                castleCounts[t.owner] += 1
                
        
        self.text.text = '<center><font size="7" color="white">Results:</font> '
        pcount = 0
        lms = -1
        for p, c in castleCounts.iteritems():
            self.text.text += '<br/><font color="{0}" size="5">'.format(
                    PlayerImages.hexColors[p.id])
            self.text.text += "{0}: ".format(p.name.upper())
            if c == 0:
                self.text.text += "DEFEATED"
                p.inGame = None
            else:
                self.text.text += "{0} CASTLES".format(c)
                pcount += 1
                lms = p
            self.text.text += '</font>'
        
        if pcount == 1:
            self.text.text += '<br/><br/><font color="{0}" size="7">'.format(
                    PlayerImages.hexColors[lms.id])
            self.text.text += '{0} WINS!</font>'.format(lms.name.upper())
        elif pcount == 0:
            self.text.text += '<br/><br/><font color="white" size="7">'
            self.text.text += 'EVERYONE LOSES!</font>'
            
        self.text.text += '</center>'
        
    
    def drawPlayer(self, p, x, y):
        self.drawCursor(p, x, y)
        
    
    def onAction(self, player, action):
        if self.timer > 0:
            return
        if action == Actions.BTN1:
            self.remove()
            pcount = 0
            for p in self.scene.app.players:
                if p.inGame:
                    pcount += 1
            if pcount > 1:
                from placeLayer import PlaceLayer
                self.scene.addLayer(PlaceLayer())
            else:
                from game import GameScene
                self.scene.app.removeScene(self.scene)
                self.scene.app.addScene(GameScene())
            
            
    def onDraw(self):
        super(ScorePhase, self).onDraw()
        self.text.draw()
            
            
    def onTimer(self):
        # Wait for a button press
        pass
    