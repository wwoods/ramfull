"""Image resources - load this file to load images."""

import pyglet
import os, sys
import re

DIR = os.path.dirname(os.path.abspath(__file__))

unknown = pyglet.image.load(os.path.join(DIR, 'tiles', 'unknown.png'))

class ImageLoader(object):
    
    IMG_FILE = re.compile(r".*\.(png)", re.I)
    
    def __init__(self, path):
        self.path = path
        self.images = pyglet.image.atlas.TextureBin()
        
        base = os.path.join(DIR, self.path)
        for p in os.listdir(base):
            pname = os.path.join(base, p)
            if (os.path.isfile(pname) 
                    and self.IMG_FILE.match(pname.lower()) is not None):
                name = self.getImageName(p)
                try:
                    img = self.images.add(pyglet.image.load(pname))
                except Exception, e:
                    print("While loading {0}: ".format(pname))
                    raise
                setattr(self, name, img)
        
    
    def __getattr__(self, name):
        return unknown
    
    
    def getImageName(self, pname):
        pname = pname[:pname.rindex('.')]
        return pname.upper().replace('-', '_')
        

TileImages = ImageLoader("tiles")
TileObjectImages = ImageLoader("tileObjs")

PlayerImages = ImageLoader("players")
# Split player cursor into 4 quadrants
def split4(name):
    ig = pyglet.image.ImageGrid(getattr(PlayerImages, name), 2, 2)
    setattr(PlayerImages, name + '_UL', ig[2])
    setattr(PlayerImages, name + '_UR', ig[3])
    setattr(PlayerImages, name + '_LR', ig[1])
    setattr(PlayerImages, name + '_LL', ig[0])
split4("PLAYER_OUTLINE")
split4("PLAYER_COLOR")

PlayerImages.colors = [ 
        (255, 0, 0), 
        (0, 255, 0), 
        (0, 0, 255),
        (255, 0, 255),
        (255, 255, 0),
        (0, 255, 255),
        ]
PlayerImages.names = [
        "red player",
        "green player",
        "blue player",
        "purple player",
        "yellow player",
        "aquamarine player",
        ]
PlayerImages.hexColors = [
        '#{0:02x}{1:02x}{2:02x}'.format(c[0], c[1], c[2])
        for c in PlayerImages.colors
        ]
