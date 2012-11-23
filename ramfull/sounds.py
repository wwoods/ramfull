
import os, re
import pyglet
DIR = os.path.dirname(os.path.abspath(__file__))

class SoundsLoader(object):
    
    IMG_FILE = re.compile(r".*\.(aif|wav|mp3|flac)", re.I)
    
    def __init__(self, path):
        self.path = path
        
        base = os.path.join(DIR, self.path)
        for p in os.listdir(base):
            pname = os.path.join(base, p)
            if (os.path.isfile(pname) 
                    and self.IMG_FILE.match(pname.lower()) is not None):
                name = self.getImageName(p)
                try:
                    img = SoundWrapper(
                            pyglet.media.load(pname, streaming = False))
                except Exception, e:
                    print("While loading {0}: ".format(pname))
                    raise
                setattr(self, name, img)
    
    
    def getImageName(self, pname):
        pname = pname[:pname.rindex('.')]
        return pname.upper().replace('-', '_')
    

# REALLY shitty sound mixer...
channels = []
for i in range(4):
    p = pyglet.media.Player()
    p.eos_action = 'stop'
    # Fill in our variables...
    p.wrapSound = None
    p.minTime = 0.0
    channels.append(p)
    
    
class SoundWrapper(object):
    def __init__(self, snd):
        self.snd = snd
        self.instances = 0
        
    
    def play(self, maxInstances = None, minTime = 9000.0, volume = 1.0):
        useChannel = None
        oldChannel = None
        oldSelfChannel = None
        okInstances = 0
        for c in channels:
            if not c.playing:
                useChannel = c
                break
            elif c.time >= c.minTime:
                if (oldChannel is None 
                        or oldChannel.time - oldChannel.minTime 
                                <= c.time - c.minTime):
                    oldChannel = c
                if c.wrapSound == self and (
                        oldSelfChannel is None
                        or oldSelfChannel.time - oldSelfChannel.minTime
                                <= c.time - c.minTime):
                    oldSelfChannel = c
            elif c.wrapSound == self:
                okInstances += 1
                
        # Limit a single sample to make sure there are channels available
        # for others...
        if maxInstances is not None:
            if self.instances >= maxInstances:
                # we MUST replace an old self, if anything
                useChannel = None
                oldChannel = oldSelfChannel
        else:
            maxInstances = okInstances + 1
            
        if useChannel is None:
            if oldChannel is None or okInstances >= maxInstances:
                # We can't play - no channel to replace, or we simply have
                # too many instances that are playing OK
                return
            useChannel = oldChannel
        
        # Using an old channel?
        if useChannel.wrapSound is not None:
            useChannel.wrapSound.instances -= 1
            
        # Pyglet's sound as of 1.2alpha1 is broken, so we have to manually
        # fast-forward... also handy in case we want to "crop" sounds
        useChannel.next()
        useChannel.queue(self.snd)
        useChannel.volume = volume
        # Only "truncate" this sound after the min time
        useChannel.minTime = min(minTime, self.snd.duration)
        useChannel.wrapSound = self
        self.instances += 1
        useChannel.play()
    
AllSounds = SoundsLoader("sounds")
