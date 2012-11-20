
import pyglet
from images import TileObjectImages

from tile import Tile

class TileObject(object):
    DEFAULT_IMAGE = TileObjectImages.UNKNOWN
    
    @property
    def tilesHigh(self):
        return int(self.DEFAULT_IMAGE.height / Tile.SIZE)
    
    @property
    def tilesWide(self):
        return int(self.DEFAULT_IMAGE.width / Tile.SIZE)
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
        
    def remove(self):
        self.sprite.delete()
        self.board.removeObj(self)
        
        
    def _tileObjectInit(self, board):
        self.board = board
        self.sprite = pyglet.sprite.Sprite(self.DEFAULT_IMAGE,
                batch = board.tileObjsBatch)
        
        
    def preDraw(self):
        """Determine which image our sprite should be using"""
        self.sprite.x = self.x * Tile.SIZE
        self.sprite.y = self.y * Tile.SIZE


class Cannon(TileObject):
    tilesWide = 2
    tilesHigh = 2
    
    DEFAULT_IMAGE = TileObjectImages.CANNON
    
    
class Castle(TileObject):
    tilesWide = 2
    tilesHigh = 2
    
    DEFAULT_IMAGE = TileObjectImages.CASTLE
    