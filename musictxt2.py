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
cde.start_chord = 'C'
'''

def g__edc__():
    yield 'efmgec--'
g__edc__.start_chord = 'C'

def fedcAcee():
    fns.chord = 'D7'
    yield '-d------'
fedcAcee.start_chord = 'Fmaj7'

if __name__ == '__main__':
    def play_loop():
        while True:
            fns.play_func( g__edc__ )
            fns.play_func( fedcAcee )
    env = globals()
    fns.setup()
    #fns.goof_around(env)
    play_loop()
    fns.console(env = env)

#done shorten cur_chord to just chord
#todo shorten fn.start_chord to just chord
#todo allow fn.start_chord to be a function
#todo decorator for start_chord
#todo only choose a new instrument if "new" is chosen as argv,
    # else keep the existing ones

