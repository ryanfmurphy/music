import music.fns as f

f.MEL_VEL = 100
f.CHORD_VEL = 70
f.SOMETIMES_DELAY = False

f.DURATION = .3

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
    yield 'cdeC-eC-'
    f.chord_to('Am')
    yield 'edcAcdee'

@f.start_chord('C')
def cH_cd_Hd():
    f.chord_to(f.options('Bb','Gm'))
    yield 'ef--'
    f.chord_to('F')
    yield '-fgh'
    f.chord_to('C')
    yield 'C--gChgf-fefgfeH'
    f.chord_to('C')
    yield 'c----cdf'
    f.chord_to(f.options('Bb','Eb'))
    yield 'hdch'
    f.chord_to('F')
    yield 'acHa'
    f.chord_to(f.options('C','Am'))
    yield 'g-edegedgCge-dcG'

if __name__ == '__main__':
    env = globals()
    f.setup()
    f.goof_around(env)
    f.console(env = env)

