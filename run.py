
import os, sys
DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DIR)
sys.path.insert(1, os.path.join(DIR, '../pyglet_piss'))

from ramfull.game import GameScene

import pyglet_piss
pyglet_piss.Actions.RECURRING_INTERVAL = 0.05
pyglet_piss.app.run(GameScene())
