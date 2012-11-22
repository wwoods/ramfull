
import random
import pyglet

from ramfull.images import PlayerImages, TileImages

class TileTypes(object):
    GRASS = 0
    SEA = 1
    MAX = 2
    
    
class Scorch(pyglet.sprite.Sprite):
    def __init__(self, x, y, batch):
        super(Scorch, self).__init__(TileImages.SCORCH, 
                x = x * Tile.SIZE, y = y * Tile.SIZE,
                batch = batch)
        pyglet.clock.schedule_once(lambda dt: self.delete(), 5.0)
        

class Tile(object):
    SIZE = 16 # px width & height of tile images
    
    def __init__(self, board, x, y, batch):
        self.neighbors = [] # Initialized by board after all tiles are 
                            # made... [ n, e, s, w ]
        self.owner = None
        self.object = None
        self.board = board
        self.isTerritory = False
        self._scorch = None
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
        
        
    def scorch(self):
        self._scorch = Scorch(self.x, self.y, self.sprite.batch)
        
        
    def setType(self, type):
        self.type = type
        self.update()
        
        
    def update(self):
        c = (255, 255, 255)
        if self.type == TileTypes.GRASS:
            if not self.isTerritory or self.owner is None:
                if (self.x + self.y) % 2 == 0:
                    i = TileImages.GRASS_EVEN
                else:
                    i = TileImages.GRASS_ODD
            else:
                c = PlayerImages.colors[self.owner.id]
                if (self.x + self.y) % 2 == 0:
                    i = TileImages.TERRITORY_EVEN
                else:
                    i = TileImages.TERRITORY_ODD
        elif self.type == TileTypes.SEA:
            if random.random() < 0.05:
                i = TileImages.SEA_ODD
            else:
                i = TileImages.SEA
        else:
            raise ValueError("Bad type: " + str(type))
        self.sprite.image = i
        self.sprite.color = c
        