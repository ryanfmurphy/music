import midi, random, fns, pdb, musictxt

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

if __name__ == '__main__':
    env = globals()
    fns.setup()
    fns.goof_around(env)
    fns.console(env = env)

