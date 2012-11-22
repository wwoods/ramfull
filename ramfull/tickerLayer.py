
import pyglet
from pyglet_piss import Layer

class TickerLayer(Layer):
    suspendsLower = True
    
    def __init__(self, text):
        Layer.__init__(self)
        self.text = text
    
    
    def _layerInit(self, scene):
        Layer._layerInit(self, scene)
        self.label = pyglet.text.Label(text = self.text,
                anchor_x = 'center', anchor_y = 'center',
                x = scene.window.width * 0.5,
                y = scene.window.height * 0.5,
                font_size = 48)
        self.time = 4.0
        self.maxTime = self.time
        
        
    def onDraw(self):
        self.label.draw()
        
        
    def onUpdate(self, dt):
        self.time -= dt
        self.label.y = self.time / self.maxTime * self.scene.window.height
        if self.time <= 0:
            self.remove()
    