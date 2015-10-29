import midi, random, fns, pdb, musictxt

def ceg():
    fns.chord = "C"
    if fns.coinflip():
        response = fns.options(*"cdefgaBC")
    else:
        response = "dBG"
        fns.chord = "G major"
    if fns.coinflip():
        return gCgfe(response)
    else:
        return response

def edceg():
    return 'fed'


def gCgfe(gef=None, fde=None):
    fns.chord = "C"
    if gef == "dBG":
        if fde == "cAG":
            return "ef|gCgfe"
        elif fde is 'fde':
            return "cAG";
        elif fde is None:
            fns.chord = "G7"
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
    fns.chord = fns.options('Dm','F','Bb')
    if fns.under_assumption('working with strings'):
        return 'fe-d--'
    else:
        return ('f','e','-','d','-','-')

def cefg():
    if fns.coinflip():
        fns.chord = fns.options('C','Em','Am','Cmaj7','Em7','Am7')
    parts = ('fed-','cBA-')
    return fns.some_parts(*parts)

def cBA_():
    fns.chord = fns.options('Am','Am7')
    parts = ('fed-', 'cdefe')
    return fns.some_parts(*parts)

def aCF(): return 'CaCf' # leading hyphen means no pause
def bDG(): return 'DbDg'
def CEA():
    fns.chord = fns.options('D7', 'Am')
    yield '-OABcAME'
    #fns.chord = fns.options('D7', 'Am')
    #yield 'cAME'
    fns.chord = fns.options('D7', 'Bm')
    yield 'D-D---'

def edc():
    if fns.coinflip():
        fns.chord = fns.options('Dm', 'G')
        return 'defg---'
    else:
        fns.chord = fns.options('C', 'Em')
        return 'efg'

def abC():
    if fns.coinflip():
        return 'b-a-g---'
    else:
        return 'b-g-e---'

def fga():
    r = random.randint(1,4)
    if r==1:
        fns.chord = fns.options('D7', 'F#m7b5', 'B7')
        return 'mga'
    elif r==2:
        fns.chord = fns.options('C','F')
        return 'gec'
    elif r==3:
        fns.chord = 'Am'
        return 'abC'
    elif r==4:
        return 'abCbabCDE-'
    else:
        raise ValueError("Unexpected random r value " + r)

def cde():
    yield "def"
    yield "efg"
    yield "fga"
    fns.chord = 'F'
    yield "gab"
    yield "abC"
    fns.chord = 'G'
    yield "bCD"
    fns.chord = fns.options('C','Am')
    yield "C"

#todo fix the octaves of the incremental yields
def cdeg():
    if fns.coinflip():
        fns.chord = 'F'
        yield "agfa"
        fns.chord = 'C'
        yield "g-c-c-c-"
        fns.chord = 'C'
        yield "cdeg"
        if fns.coinflip():
            fns.chord = 'F'
            yield "agfe"
            fns.chord = 'G'
            yield "d---"
        else:
            fns.chord = 'F'
            yield "agec"
            fns.chord = 'D7'
            yield "d-cd"
            fns.chord = 'E7'
            yield "e-seE_De"
            fns.chord = fns.options('Am','F')
            yield "C-a-"
    else:
        yield "fedc"
        yield "edcA"
        yield "GAFG"
        yield "EGcB"
        fns.chord = 'Am'
        yield "cAEG"
        fns.chord = 'D'
        yield "MAdr"
        fns.chord = 'G'
        yield "dBGB"
        fns.chord = 'E7'
        yield "OBed"
        fns.chord = 'Am'
        yield "c-A-"

def _EDE():
    fns.chord = fns.options('F7','Fm7','D7')
    if fns.chord == 'Fm7':
        yield "SDCo"
    else:
        yield "SDCa"
    yield "gsdc"
    fns.chord = fns.options('D7','Dm7','Gm7')
    yield "A-_aCD-a"
    fns.chord = fns.options('Am7','Gm7')
    #yield None

def gedc():
    if fns.coinflip():
        fns.chord = fns.options('Am','Am7','F','Fmaj7','Dm','Dm7','D7',)
    return 'AcdeA-A'

def fedc():
    fns.chord = fns.options('Fm','Fm7','F minor major 7','Dm7b5', 'Bb7')
    yield 'ogf'
    yield 'goC'
    if fns.chord in ('Fm7', 'Bb7'):
        yield 'DSDoC--'
    else:
        yield 'DEDoC--'
    if fns.coinflip():
        fns.chord = fns.options('F','Dm','C','Em7')

def gbDEFESEG_EE_D__():
    fns.chord = 'Fmaj7'
    return 'E-CC--Cba-E-D-g-'

def abCD():
    chords = iter(fns.options(
        ('F','G','D','E','Am'),
        ('Dm','E','F','G','Am'),
        ('C','G','E7','E7','D7'),
    ))
    melody = iter(('E-EE','D-ED','Cb','ab','C-a-'))
    for melpart in melody:
        fns.chord = chords.next()
        yield melpart

def Cbag():
    fns.chord = 'D7'
    yield 'mEDC'
    fns.chord = 'G7'
    yield 'bagf'
    fns.chord = 'E7'
    yield 'eDCb'
    fns.chord = 'Am'
    yield 'a---'

def efede():
    speed = fns.options(.3,.2,.1)
    fns.change_duration(speed)

def edcAc_A():
    fns.chord = 'Am'
    return 'f--edcAAA'

def gagededc():
    fns.chord = 'Am'
    return '-cdceedc'

def daaaCb_a():
    fns.chord = 'D7'
    return '-AAAcdeg'

def gcccsd_c():
    fns.chord = 'Cm'
    yield '-cccsfgH'
    fns.chord = 'Bb'
    yield '-hhhDSFO'
    fns.chord = 'Ab'
    yield '-oooCDSG'
    fns.chord = 'Fm'
    yield '-OGF-S-C'
    yield '-dsH-G--'
gcccsd_c.start_chord = 'Cm'
    

if __name__ == '__main__':
    env = globals()
    #names = ('gcccsd_c', 'daaaCb_a', 'gagededc', 'edcAc_A')
    #env = fns.take_from_env(names, globals())
    fns.setup()
    fns.goof_around(env)
    fns.console(env = env)

