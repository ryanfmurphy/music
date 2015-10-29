import midi, random, fns, pdb, musictxt

#fns.DURATION = midi.swung_dur(.3,.15).next
fns.SOMETIMES_DELAY = False

def __f__d__A__GA___():
    yield '--f--d--A-------'
__f__d__A__GA___.start_chord = 'Dm'

def __m__m__m__gm___():
    fns.cur_chord = 'C'
    yield '--e--e--'
    fns.cur_chord = 'G'
    yield 'd-------'
__m__m__m__gm___.start_chord = 'D'

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

#todo shorted cur_chord and start_chord to just chord
#todo allow fn.start_chord to be a function
#todo decorator for start_chord
#todo only choose a new instrument if "new" is chosen as argv,
    # else keep the existing ones

