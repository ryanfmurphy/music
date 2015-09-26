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

def aCF(): return 'CaCf' # leading hyphen means no pause
def bDG(): return 'DbDg'
def CEA():
    fns.cur_chord = fns.options('D7', 'Am')
    yield '-OAB'
    fns.cur_chord = fns.options('D7', 'Am')
    yield 'cAME'
    fns.cur_chord = fns.options('D7', 'Bm')
    yield 'D-D---'

def edc():
    if fns.coinflip():
        fns.cur_chord = fns.options('Dm', 'G')
        return 'defg---'
    else:
        fns.cur_chord = fns.options('C', 'Em')
        return 'efg'

def abC():
    if fns.coinflip():
        return 'b-a-g---'
    else:
        return 'b-g-e---'

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
    fns.cur_chord = fns.options('C','Am')
    yield "C"

#todo fix the octaves of the incremental yields
def cdeg():
    if fns.coinflip():
        fns.cur_chord = 'F'
        yield "agfa"
        fns.cur_chord = 'C'
        yield "g-c-c-c-"
        fns.cur_chord = 'C'
        yield "cdeg"
        fns.cur_chord = 'F'
        yield "agfe"
        fns.cur_chord = 'G'
        yield "d---"
    else:
        yield "fedc"
        yield "edcA"
        yield "GAFG"
        yield "EGcB"
        fns.cur_chord = 'Am'
        yield "cAEG"
        fns.cur_chord = 'D'
        yield "MAdr"
        fns.cur_chord = 'G'
        yield "dBGB"
        fns.cur_chord = 'E7'
        yield "OBed"
        fns.cur_chord = 'Am'
        yield "c-A-"

def gedc():
    if fns.coinflip():
        fns.cur_chord = fns.options('Am','Am7','F','Fmaj7','Dm','Dm7','D7',)
    return 'AcdeA-A'

def fedc():
    fns.cur_chord = fns.options('Fm','Fm7','F minor major 7','Dm7b5', 'Bb7')
    yield 'ogf'
    yield 'goC'
    if fns.cur_chord in ('Fm7', 'Bb7'):
        yield 'DSDoC--'
    else:
        yield 'DEDoC--'
    if fns.coinflip():
        fns.cur_chord = fns.options('F','Dm','C','Em7')

if __name__ == '__main__':
    env = globals()
    #names = ('cde','cdeg')
    #env = fns.take_from_env(names, globals())
    fns.setup()
    fns.goof_around(env)
    fns.console(env = env)

