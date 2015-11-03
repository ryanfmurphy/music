import music, random, pdb, musictxt
import music.fns as f

f.MEL_VEL = 127
f.DURATION = music.swung_dur(.3,.15).next
f.SOMETIMES_DELAY = False
f.INSTRUMENTS = (24, 49)

'''
def cde():
    yield 'def'
    yield 'efg'
    if f.coinflip():
        yield 'fga'
        f.chord = 'F'
        yield 'gab'
        yield 'abC'
        f.chord = 'G'
        yield 'bCD'
        f.chord = 'C'
        yield 'C--'
    else:
        yield 'fed'
        f.chord = 'Dm'
        yield 'edc'
        f.chord = 'G'
        yield 'dcB'
        f.chord = 'C'
        yield 'c-----'
cde.chord = 'C'
'''

@f.start_chord('C')
def g__edc__():
    yield 'efmgec--'

@f.start_chord('Fmaj7')
def fedcAcee():
    f.chord = 'D7'
    yield '-d------'

if __name__ == '__main__':
    def play_loop():
        try: 
            while True:
                f.play_func( g__edc__ )
                f.play_func( fedcAcee )
        except KeyboardInterrupt:
            music.panic()
            
    env = globals()
    f.setup()
    #f.goof_around(env)
    play_loop()
    f.console(env = env)

