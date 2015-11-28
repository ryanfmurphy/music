import random, pdb
import music.fns as f, subprocess as sp

f.MEL_VEL = 100
f.CHORD_VEL = 60

f.SOMETIMES_DELAY = False
f.INSTRUMENTS = (24, 49)
f.DURATION = .4

@f.start_chord('Am')
def cde():
    yield 'efg'

@f.start_chord('F')
def Cag():
    yield 'efc'

@f.start_chord('Bbmaj7')
def a_g_f_():
    if f.coinflip():
        return 'e-d-c-'
    else:
        return 'edcHA-'

"""
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

"""

#exec(sp.check_output(['php', 'music_fns.py.php']))

if __name__ == '__main__':
    env = globals()
    #names = ('c_eg','edcd','fedc','eses')
    #env = f.take_from_env(names, globals())
    f.setup()
    f.goof_around(env)
    f.console(env = env)


