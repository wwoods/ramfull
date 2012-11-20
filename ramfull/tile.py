
import random
import pyglet

from ramfull.images import TileImages

class TileTypes(object):
    GRASS = 0
    SEA = 1
    MAX = 2
        

class Tile(object):
    SIZE = 16 # px width & height of tile images
    
    def __init__(self, board, x, y, batch):
        self.neighbors = [] # Initialized by board after all tiles are 
                            # made... [ n, e, s, w ]
        self.owner = None
        self.object = None
        self.board = board
        self.x = x
        self.y = y
        # For generation; the castle grounds that this tile belongs to, if 
        # any
        self.gen_castleGrounds = None
        self.sprite = pyglet.sprite.Sprite(
                TileImages.GRASS,
                x = x * self.SIZE, y = y * self.SIZE, 
                batch = batch
        )
        self.setType(TileTypes.GRASS)
        
        
    def setType(self, type):
        self.type = type
        self.update()
        
        
    def update(self):
        if self.type == TileTypes.GRASS:
            if (self.x + self.y) % 2 == 0:
                i = TileImages.GRASS_EVEN
            else:
                i = TileImages.GRASS_ODD
        elif self.type == TileTypes.SEA:
            if random.random() < 0.05:
                i = TileImages.SEA_ODD
            else:
                i = TileImages.SEA
        elif self.type == TileTypes.WALL:
            m = tuple(True if t and t.type == TileTypes.WALL else False 
                      for t in self.neighbors)
            i = {
                 ( False, False, False, False ): TileImages.WALL_ALONE,
                 ( True, False, False, False): TileImages.WALL_VERT,
                 ( False, True, False, False): TileImages.WALL_HORZ,
                 ( True, True, False, False): TileImages.WALL_NE,
                 ( False, False, True, False): TileImages.WALL_VERT,
                 ( True, False, True, False): TileImages.WALL_VERT,
                 ( False, True, True, False): TileImages.WALL_SE,
                 ( True, True, True, False): TileImages.WALL_E,
                 ( False, False, False, True): TileImages.WALL_HORZ,
                 ( True, False, False, True): TileImages.WALL_NW,
                 ( False, True, False, True): TileImages.WALL_HORZ,
                 ( True, True, False, True): TileImages.WALL_N,
                 ( False, False, True, True): TileImages.WALL_SW,
                 ( True, False, True, True): TileImages.WALL_W,
                 ( False, True, True, True): TileImages.WALL_S,
                 ( True, True, True, True): TileImages.WALL_ALONE,
                 }[m]
            i = TileImages.WALL_ALONE
        else:
            raise ValueError("Bad type: " + str(type))
        self.sprite.image = i
        