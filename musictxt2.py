import midi, random, fns, pdb, musictxt

fns.DURATION = midi.swung_dur(.3,.15).next
fns.SOMETIMES_DELAY = False

'''
def cde():
    yield 'def'
    yield 'efg'
    if fns.coinflip():
        yield 'fga'
        fns.cur_chord = 'F'
        yield 'gab'
        yield 'abC'
        fns.cur_chord = 'G'
        yield 'bCD'
        fns.cur_chord = 'C'
        yield 'C--'
    else:
        yield 'fed'
        fns.cur_chord = 'Dm'
        yield 'edc'
        fns.cur_chord = 'G'
        yield 'dcB'
        fns.cur_chord = 'C'
        yield 'c-----'
cde.start_chord = 'C'
'''

def g__edc__():
    yield 'efmgec--'
g__edc__.start_chord = 'C'

def fedcAcee():
    fns.cur_chord = 'D7'
    yield '-d------'
fedcAcee.start_chord = 'Fmaj7'

if __name__ == '__main__':
    env = globals()
    fns.setup()
    fns.goof_around(env)
    fns.console(env = env)

#todo shorted cur_chord and start_chord to just chord
#todo allow fn.start_chord to be a function
#todo decorator for start_chord
#todo only choose a new instrument if "new" is chosen as argv,
    # else keep the existing ones

