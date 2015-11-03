import midi, random, pdb, musictxt
import fns as f, subprocess as sp

f.SOMETIMES_DELAY = False
f.INSTRUMENTS = (24, 49)
#f.INSTRUMENTS = (61, 73)
f.DURATION = .1

f.MEL_VEL = 127
f.CHORD_VEL = 70

@f.start_chord('Am')
def cde():
    f.chord = f.options('C', 'F', 'Em')
    if f.coinflip():
        yield 'efg'
    else:
        yield 'gfe'
    f.chord = f.options('C', 'F', 'Em')
    if f.coinflip():
        yield 'gaC'
    else:
        yield 'Cag'

def abCDEFG():
    f.chord = f.options('G', 'B', 'D')
    r = random.randint(0,6)
    if r == 0:
        yield 'a'
    elif r == 1:
        yield 'b' 
    elif r == 2:
        yield 'C'
    elif r == 3:
        yield 'D'
    elif r == 4:
        yield 'E'
    elif r == 5:
        yield 'F' 
    elif r == 6:
        yield 'G'

def EFEFEDE_b_g_():
    return 'ababaga-E-E-'

def GAGADBG_b_g_():
    return 'ababaga-E-E-'

exec(sp.check_output(['php', 'music_fns.py.php']))

if __name__ == '__main__':
    env = globals()
    #names = ('c_eg','edcd','fedc','eses')
    #env = f.take_from_env(names, globals())
    f.setup()
    f.goof_around(env)
    f.console(env = env)


