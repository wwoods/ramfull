
import math

import pyglet
from pyglet_piss import Actions, Layer

from ramfull.tile import Tile, TileTypes
from ramfull.images import PlayerImages
from tickerLayer import TickerLayer

class GamePhaseLayer(Layer):
    """Any layer that shows the players' cursors should derive from this.
    
    Subclasses must define drawPlayer(p), which should probably call 
    drawCursor.
    """
    
    TICKER = "TICKER"
    TIMER = 100.0
    
    def _layerInit(self, scene):
        Layer._layerInit(self, scene)
        
        self.cursor = pyglet.sprite.Sprite(PlayerImages.PLAYER_OUTLINE)
        self.board = self.scene.board
        if self.TICKER is not None:
            self.scene.addLayer(TickerLayer(self.TICKER))
        
        self.timer = self.TIMER
        self.timerLabel = pyglet.text.Label(anchor_x = 'center', 
                anchor_y = 'top')
    
    
    def drawCursor(self, p, x, y):
        self.cursor.image = PlayerImages.PLAYER_OUTLINE
        self.cursor.color = PlayerImages.colors[p.id]
        self.cursor.x = x
        self.cursor.y = y
        self.cursor.draw()
        
        self.cursor.image = PlayerImages.PLAYER_COLOR
        self.cursor.color = (255, 255, 255)
        self.cursor.draw()
        
        
    def drawCursorCorner(self, p, x, y, orient):
        """orient - one of ul, ur, lr, ll, specifying the corner of the cursor
        to be drawn.
        """
        oi = None
        ci = None
        xo = 0
        yo = 0
        if orient == 'ul':
            oi = PlayerImages.PLAYER_OUTLINE_UL
            ci = PlayerImages.PLAYER_COLOR_UL
            yo = Tile.SIZE * 0.5
        elif orient == 'ur':
            oi = PlayerImages.PLAYER_OUTLINE_UR
            ci = PlayerImages.PLAYER_COLOR_UR
            xo = Tile.SIZE * 0.5
            yo = Tile.SIZE * 0.5
        elif orient == 'lr':
            oi = PlayerImages.PLAYER_OUTLINE_LR
            ci = PlayerImages.PLAYER_COLOR_LR
            xo = Tile.SIZE * 0.5
        elif orient == 'll':
            oi = PlayerImages.PLAYER_OUTLINE_LL
            ci = PlayerImages.PLAYER_COLOR_LL
        else:
            raise ValueError("Unknown orient: " + str(orient))
        
        self.cursor.image = oi
        self.cursor.color = PlayerImages.colors[p.id]
        self.cursor.x = x + xo
        self.cursor.y = y + yo
        self.cursor.draw()
        
        self.cursor.image = ci
        self.cursor.color = (255, 255, 255)
        self.cursor.draw()
            
            
    def drawCursorLarge(self, p, x, y, tw, th):
        """Draw a multi-tile, rectangular cursor.
        """
        rx = x + (tw - 1) * Tile.SIZE
        ry = y + (th - 1) * Tile.SIZE
        self.drawCursorCorner(p, x, y, 'll')
        self.drawCursorCorner(p, rx, y, 'lr')
        self.drawCursorCorner(p, rx, ry, 'ur')
        self.drawCursorCorner(p, x, ry, 'ul')
    
    
    def drawPlayer(self, p, x, y):
        """Draw this player's cursor at the current position"""
        raise NotImplementedError()
        
        
    def onAction(self, player, action):
        if not player.inGame:
            return
        
        if action == Actions.TAP_UP:
            player.inGame.y += 1
            player.inGame.y = min(player.inGame.y, self.board.height - 1)
        elif action == Actions.TAP_DOWN:
            player.inGame.y -= 1
            player.inGame.y = max(player.inGame.y, 0)
        elif action == Actions.TAP_LEFT:
            player.inGame.x -= 1
            player.inGame.x = max(player.inGame.x, 0)
        elif action == Actions.TAP_RIGHT:
            player.inGame.x += 1
            player.inGame.x = min(player.inGame.x, self.board.width - 1)
        else:
            return
        return True
    
    
    def onDraw(self):
        for p in self.scene.app.players:
            if not p.inGame:
                continue
            self.drawPlayer(p, p.inGame.x * Tile.SIZE, p.inGame.y * Tile.SIZE)
            
        if self.timer is not None:
            self.timerLabel.x = self.scene.window.width * 0.5
            self.timerLabel.y = self.scene.window.height
            toShow = abs(max(math.ceil(self.timer), 0))
            self.timerLabel.text = "{0:0.0f}".format(toShow)
            self.timerLabel.font_size = 36
            self.timerLabel.draw()
        
        
    def onTimer(self):
        raise NotImplementedError()
        
        
    def onUpdate(self, dt):
        if self.timer is not None:
            self.timer -= dt
            if self.timer <= 0:
                self.timer = None
                self.onTimer()
        