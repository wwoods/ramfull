
import pyglet
from pyglet_piss import Actions
from ramfull.player import RamfullPlayer
from gamePhaseLayer import GamePhaseLayer
from selectCastle import SelectCastleLayer

class OptInLayer(GamePhaseLayer):
    TICKER = None
    TIMER = None
    
    def _layerInit(self, scene):
        super(OptInLayer, self)._layerInit(scene)
        self._playersAdded = 0
        self.caption = pyglet.text.Label("Press Any Button to Join",
                x = self.window.width * 0.5, y = self.window.height * 0.5,
                anchor_x = 'center', anchor_y = 'center',
                font_size = 36)
        self.timerFastUntil = 900
    
    def drawPlayer(self, p, x, y):
        self.drawCursor(p, x, y)
        
        
    def onAction(self, player, action):
        if action == Actions.BTN1 or action == Actions.BTN2:
            if player.inGame is None:
                player.inGame = RamfullPlayer()
                self._playersAdded += 1
                if self.timer is None and self._playersAdded >= 2:
                    self.timer = 20.0
            elif self.timer is not None:
                self.timerFastUntil = self.timer - 1.0
        else:
            return super(OptInLayer, self).onAction(player, action)
        return True
    
    
    def onDraw(self):
        super(OptInLayer, self).onDraw()
        self.caption.draw()
            
            
    def onTimer(self):
        self.remove()
        self.scene.remakeBoard()
        self.scene.addLayer(SelectCastleLayer())
        
        
    def onUpdate(self, dt):
        if self.timer >= self.timerFastUntil:
            dt *= 8
        super(OptInLayer, self).onUpdate(dt)