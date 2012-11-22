import sys
import os

import pyglet
from cocos.director import director
from cocos.layer import Layer
from cocos.scene import Scene

class MyLayer(Layer):
    is_event_handler = True

    def __init__(self, t):
        super(MyLayer, self).__init__()
        self.t = t

        self.label = pyglet.text.Label(self.t)

    def on_enter(self):
        super(MyLayer, self).on_enter()

    def draw(self):
        self.label.draw()

director.init(resizable = True, caption = 'Cocos test')
director.run(Scene(MyLayer('a'), MyLayer('b')))
