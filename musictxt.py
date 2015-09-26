import midi, types, random, fns, pdb, musictxt

def ceg():
    fns.cur_chord = "C"
    if fns.coinflip():
        response = fns.options(*"cdefgaBC")
    else:
        response = "dBG"
        fns.cur_chord = "G major"
    if fns.coinflip():
        return gCgfe(response)
    else:
        return response

def edceg():
    return 'fed'


def gCgfe(gef=None, fde=None):
    fns.cur_chord = "C"
    if gef == "dBG":
        if fde == "cAG":
            return "ef|gCgfe"
        elif fde is 'fde':
            return "cAG";
        elif fde is None:
            fns.cur_chord = "G7"
            return 'fde-cAG-';

    if fde == "gafed":
        return "G-G-G---"
    elif (gef,fde) == ('d','e'):
        return 'c','A'
    else:
        return fns.options("c","G",
                        "cde","fed","Bcd","edc",
                        "egC","def","faD","efg",
                        "abC","baf","ede","eeA")

def edcHA():
    fns.cur_chord = fns.options('Dm','F','Bb')
    if fns.under_assumption('working with strings'):
        return 'fe-d'
    else:
        return ('f','e',None,'d')

def cefg():
    if fns.coinflip():
        fns.cur_chord = fns.options('C','Em','Am','Cmaj7','Em7','Am7')
    parts = ('fed-','cBA-')
    return fns.some_parts(*parts)

def cBA_():
    fns.cur_chord = fns.options('Am','Am7')
    parts = ('fed-', 'cdefe')
    return fns.some_parts(*parts)

def aCF(): return '-CaCf' # leading hyphen means no pause
def bDG(): return '-DbDg'
def CEA():
    fns.cur_chord = fns.options('D7', 'Am')
    return '-OABcAMED-D---'

def edc():
    if fns.coinflip():
        fns.cur_chord = fns.options('Dm', 'G')
        return '-defg---'
    else:
        fns.cur_chord = fns.options('C', 'Em')
        return 'efg'

def abC():
    if fns.coinflip():
        return '-b-a-g---'
    else:
        return '-b-g-e---'

def fga():
    r = random.randint(1,4)
    if r==1:
        fns.cur_chord = fns.options('D7', 'F#m7b5', 'B7')
        return 'mga'
    elif r==2:
        fns.cur_chord = fns.options('C','F')
        return 'gec'
    elif r==3:
        fns.cur_chord = 'Am'
        return 'abC'
    elif r==4:
        return 'abCbabCDE-'
    else:
        raise ValueError("Unexpected random r value " + r)

def cde():
    yield "def"
    yield "efg"
    yield "fga"
    fns.cur_chord = 'F'
    yield "gab"
    yield "abC"
    fns.cur_chord = 'G'
    yield "bCD"
    fns.cur_chord = 'C'
    yield "C"

if __name__ == '__main__':
    env = globals()
    #names = ('ceg',)
    #env = fns.take_from_env(names, globals())
    fns.setup()
    fns.goof_around(env)
    fns.console(env = env)

