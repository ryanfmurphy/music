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
        return 'fe-d--'
    else:
        return ('f','e','-','d','-','-')

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
    yield '-OABcAME'
    #fns.cur_chord = fns.options('D7', 'Am')
    #yield 'cAME'
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
        if fns.coinflip():
            fns.cur_chord = 'F'
            yield "agfe"
            fns.cur_chord = 'G'
            yield "d---"
        else:
            fns.cur_chord = 'F'
            yield "agec"
            fns.cur_chord = 'D7'
            yield "d-cd"
            fns.cur_chord = 'E7'
            yield "e-seEeDe"
            fns.cur_chord = fns.options('Am','F')
            yield "C-a-"
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

def _EDE():
    fns.cur_chord = fns.options('F7','Fm7','D7')
    if fns.cur_chord == 'Fm7':
        yield "SDCo"
    else:
        yield "SDCa"
    yield "gsdc"
    fns.cur_chord = fns.options('D7','Dm7','Gm7')
    yield "A-_aCD-a"
    fns.cur_chord = fns.options('Am7','Gm7')
    #yield None

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

def gbDEFESEG_EE_D__():
    fns.cur_chord = 'Fmaj7'
    return 'E-CC--Cba-E-D-g-'

def abCD():
    chords = iter(fns.options(
        ('F','G','D','E','Am'),
        ('Dm','E','F','G','Am'),
        ('C','G','E7','E7','D7'),
    ))
    melody = iter(('E-EE','D-ED','Cb','ab','C-a-'))
    for melpart in melody:
        fns.cur_chord = chords.next()
        yield melpart

def Cbag():
    fns.cur_chord = 'D7'
    yield 'mEDC'
    fns.cur_chord = 'G7'
    yield 'bagf'
    fns.cur_chord = 'E7'
    yield 'eDCb'
    fns.cur_chord = 'Am'
    yield 'a---'

if __name__ == '__main__':
    env = globals()
    #names = ('abCD','Cbag',)
    #env = fns.take_from_env(names, globals())
    fns.setup()
    fns.goof_around(env)
    fns.console(env = env)

