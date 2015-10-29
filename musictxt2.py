import midi, random, fns, pdb, musictxt

fns.DURATION = midi.swung_dur(.3,.15).next
fns.SOMETIMES_DELAY = False

'''
def cde():
    yield 'def'
    yield 'efg'
    if fns.coinflip():
        yield 'fga'
        fns.chord = 'F'
        yield 'gab'
        yield 'abC'
        fns.chord = 'G'
        yield 'bCD'
        fns.chord = 'C'
        yield 'C--'
    else:
        yield 'fed'
        fns.chord = 'Dm'
        yield 'edc'
        fns.chord = 'G'
        yield 'dcB'
        fns.chord = 'C'
        yield 'c-----'
cde.chord = 'C'
'''

@fns.start_chord('C')
def g__edc__():
    yield 'efmgec--'

@fns.start_chord('Fmaj7')
def fedcAcee():
    fns.chord = 'D7'
    yield '-d------'

if __name__ == '__main__':
    def play_loop():
        try: 
            while True:
                fns.play_func( g__edc__ )
                fns.play_func( fedcAcee )
        except KeyboardInterrupt:
            midi.panic()
            
    env = globals()
    fns.setup()
    #fns.goof_around(env)
    play_loop()
    fns.console(env = env)

#todo continuous octave streaming from one fn / yield to the next (or some option to do it)
#todo only choose a new instrument if "new" is chosen as argv,
    # else keep the existing ones

