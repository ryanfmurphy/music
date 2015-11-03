import random, pdb, musictxt
import music.fns as fns

fns.DURATION = .3
#fns.DURATION = midi.swung_dur(.3,.15).next
fns.SOMETIMES_DELAY = False

def m___m___m___m___():
    fns.chord = 'G'
    yield '----------------'
m___m___m___m___.chord = 'D'

if __name__ == '__main__':
    def play_loop():
        while True:
            fns.play_func( m___m___m___m___ )
    env = globals()
    fns.setup()
    #fns.goof_around(env)
    play_loop()
    fns.console(env = env)

