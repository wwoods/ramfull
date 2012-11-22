
from pyglet_piss import Actions
from placeLayer import PlaceLayer
from gamePhaseLayer import GamePhaseLayer
from tileObject import Castle

class SelectCastleLayer(GamePhaseLayer):
    TICKER = "SELECT A CASTLE"
    TIMER = 20.0
    
    def _layerInit(self, scene):
        GamePhaseLayer._layerInit(self, scene)
        
        self._playerMap = {}
        for p in scene.app.players:
            if not p.inGame:
                continue
            castles = []
            for c in scene.board.tileObjs:
                if isinstance(c, Castle):
                    t = scene.board.get(c.x, c.y)
                    if t.owner == p:
                        castles.append(c)
            self._playerMap[p] = { 'castles': castles, 'walls': [] }
            self._cycle(p, 1)
        
        
    def drawPlayer(self, p, x, y):
        if self._playerMap[p].get('isDone'):
            self.drawCursor(p, x, y)
        else:
            self.drawCursorLarge(p, x, y, 2, 2)
        
        
    def onAction(self, player, action):
        if not player.inGame:
            return False
        
        if self._playerMap[player].get('isDone'):
            return True
        
        if action == Actions.TAP_LEFT or action == Actions.TAP_UP:
            self._cycle(player, -1)
        elif action == Actions.TAP_RIGHT or action == Actions.TAP_DOWN:
            self._cycle(player, 1)
        elif action == Actions.BTN1:
            self._playerMap[player]['isDone'] = True
        else:
            return False
        return True
    
    
    def onTimer(self):
        self.remove()
        self.scene.addLayer(PlaceLayer())
    
    
    def onUpdate(self, dt):
        super(SelectCastleLayer, self).onUpdate(dt)
        
        allDone = True
        for p in self.scene.app.players:
            if not p.inGame:
                continue
            if not self._playerMap[p].get('isDone'):
                allDone = False
                break
        if allDone:
            self.onTimer()
    
    
    def _cycle(self, p, diff):
        ci = -1
        pi = self._playerMap[p]
        for i, c in enumerate(pi['castles']):
            if c.x == p.inGame.x and c.y == p.inGame.y:
                ci = i
                break
        nci = (ci + diff)
        numCastle = len(pi['castles'])
        if nci < 0:
            nci += numCastle
        elif nci >= numCastle:
            nci -= numCastle
        c = pi['castles'][nci]
        p.inGame.x = c.x
        p.inGame.y = c.y
        
        if ci >= 0:
            oc = pi['castles'][ci]
            oc.groundsRemove()
                    
        # Add new walls and territory
        c.groundsAdd()
        
    
    