
import os, sys
DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DIR)
sys.path.insert(1, os.path.join(DIR, '../pyglet_piss'))

from ramfull.game import GameScene

import pyglet_piss
pyglet_piss.Actions.RECURRING_INTERVAL = 0.05
conf = pyglet_piss.Config()
conf.merge('game.ini', noExistOk = True)
conf.merge('game_local.ini', noExistOk = True)
conf.save('game_local.ini')

import statprof
statprof.start()
pyglet_piss.app.run(conf, GameScene())
statprof.stop()
statprof.display()