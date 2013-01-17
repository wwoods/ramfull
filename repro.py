
import os, re
import pyglet
import time
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
for i in range(14):
    p = pyglet.media.Player()
    p.eos_action = 'stop'
    # Fill in our variables...
    p.wrapSound = None
    p.minEndTime = 0.0
    channels.append(p)
    
    
class SoundWrapper(object):
    def __init__(self, snd):
        self.snd = snd
        self.instances = 0
        
    
    def play(self, maxInstances = None, minTime = 9000.0, volume = 1.0):
        """NOTE - AVOID all pyglet OpenAL properties, that driver is shit.
        """
        useChannel = None
        oldChannel = None
        oldSelfChannel = None
        okInstances = 0
        now = time.time()
        for c in channels:
            if c.minEndTime == 0:
                useChannel = c
                break
            elif now >= c.minEndTime:
                if (oldChannel is None 
                        or now - oldChannel.minEndTime 
                                <= now - c.minEndTime):
                    oldChannel = c
                if c.wrapSound == self and (
                        oldSelfChannel is None
                        or now - oldSelfChannel.minEndTime
                                <= now - c.minEndTime):
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
        
        # Using an old channel?  Has it played?  Clean it.
        if useChannel.wrapSound is not None:
            useChannel.wrapSound.instances -= 1
            useChannel._audio_player.delete()
            useChannel.__init__()
            
        # Queue the sound, set it up, and go!
        useChannel.queue(self.snd)
        useChannel.volume = volume
        # Only "truncate" this sound after the min time
        useChannel.minEndTime = now + min(minTime, self.snd.duration)
        useChannel.wrapSound = self
        self.instances += 1
        SoundWrapper.numPlayed = getattr(SoundWrapper, 'numPlayed', 0) + 1
        print("Played " + str(SoundWrapper.numPlayed))
        useChannel.play()
    
AllSounds = SoundsLoader("testSounds")


def update(dt):
    AllSounds.HIT.play(minTime=0.01)
    
pyglet.clock.schedule(update)
pyglet.window.Window()
pyglet.app.run()