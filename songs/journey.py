import music.fns as f

f.MEL_VEL = 100
f.CHORD_VEL = 60
f.SOMETIMES_DELAY = False

@f.start_chord('C')
def cdefgfga():
    f.chord_to('Bb')
    yield 'h-dh'
    f.chord_to('F')
    yield 'afcA'
    f.chord_to('C')
    yield 'fecGFEc--GAcegbC'
    f.chord_to('C')
    yield 'EG ECgec'
    f.chord_to('Bb')
    yield 'hDhf'
    f.chord_to('F')
    yield 'afcA'
    f.chord_to('C')
    yield 'cdeC-eC-edcAcdee'

if __name__ == '__main__':
    env = globals()
    f.setup()
    f.goof_around(env)
    f.console(env = env)

