import music, random, pdb, musictxt
import music.fns as fns

#fns.DURATION = music.swung_dur(.3,.15).next
fns.SOMETIMES_DELAY = False

def __f__d__A__GA___():
    yield '--f--d--A-------'
__f__d__A__GA___.chord = 'Dm'

def __m__m__m__gm___():
    fns.chord = 'C'
    yield '--e--e--'
    fns.chord = 'G'
    yield 'd-------'
__m__m__m__gm___.chord = 'D'

if __name__ == '__main__':
    def play_loop():
        while True:
            #for i in range(4):
            #    fns.play_func( __f__d__A__GA___ )
            for i in range(4):
                fns.play_func( __m__m__m__gm___ )
    env = globals()
    fns.setup()
    #fns.goof_around(env)
    play_loop()
    fns.console(env = env)

