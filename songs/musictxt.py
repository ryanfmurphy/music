import music, random, pdb
import music.fns as fns

#fns.PAUSE_DISABLED = False

def ceg():
    fns.chord_to("C")
    if fns.coinflip():
        response = fns.options(*"cdefgaBC")
    else:
        response = "dBG"
        fns.chord_to("G major")
    if fns.coinflip():
        return gCgfe(response)
    else:
        return response

def edceg():
    return 'fed'


@fns.start_chord('C')
def gCgfe(gef=None, fde=None):
    fns.chord_to("C")
    if gef == "dBG":
        if fde == "cAG":
            return "ef|gCgfe"
        elif fde is 'fde':
            return "cAG";
        elif fde is None:
            fns.chord_to("G7")
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

@fns.start_chord('C7')
def edcHA_():
    fns.chord_to(fns.options('Dm','F','Bb'))
    if fns.under_assumption('working with strings'):
        return 'fe-d--'
    else:
        return ('f','e','-','d','-','-')

def cefg():
    if fns.coinflip():
        fns.chord_to(fns.options('C','Em','Am','Cmaj7','Em7','Am7'))
    parts = ('fed-','cBA-')
    return fns.some_parts(*parts)

def cBA_():
    fns.chord_to(fns.options('Am','Am7'))
    parts = ('fed-', 'cdefe')
    return fns.some_parts(*parts)

def aCF(): return 'CaCf-'
def bDG(): return 'DbDg-'
def CEA():
    fns.choose_instruments(['rnd'])
    fns.chord_to(fns.options('D7', 'Am'))
    yield '-OABcAME'
    #fns.chord_to(fns.options('D7', 'Am'))
    #yield 'cAME'
    fns.chord_to(fns.options('D7', 'Bm'))
    yield 'D-D---'

def edc():
    fns.choose_instruments(['rnd'])
    if fns.coinflip():
        fns.chord_to(fns.options('Dm', 'G'))
        return 'defg---'
    else:
        fns.chord_to(fns.options('C', 'Em'))
        return 'efg'

def abC():
    fns.choose_instruments(['rnd'])
    if fns.coinflip():
        return 'b-a-g---'
    else:
        return 'b-g-e---'

def fga():
    fns.choose_instruments(['rnd'])
    r = random.randint(1,4)
    if r==1:
        fns.chord_to(fns.options('D7', 'F#m7b5', 'B7'))
        return 'mga'
    elif r==2:
        fns.chord_to(fns.options('C','F'))
        return 'gec'
    elif r==3:
        fns.chord_to('Am')
        return 'abC'
    elif r==4:
        return 'abCbabCDE-'
    else:
        raise ValueError("Unexpected random r value " + r)

@fns.start_chord(lambda: fns.options('C','Am'))
def cde():
    fns.choose_instruments(['rnd'])
    yield "def"
    yield "efg"
    yield "fga"
    fns.chord_to('F')
    yield "gab"
    yield "abC"
    fns.chord_to('G')
    yield "bCD"
    fns.chord_to(fns.options('C','Am'))
    yield "C--"

#todo fix the octaves of the incremental yields
def cdeg():
    fns.choose_instruments(['rnd'])
    if fns.coinflip():
        fns.chord_to('F')
        yield "agfa"
        fns.chord_to('C')
        yield "g-c-c-c-"
        fns.chord_to('C')
        yield "cdeg"
        if fns.coinflip():
            fns.chord_to('F')
            yield "agfe"
            fns.chord_to('G')
            yield "d---"
        else:
            fns.chord_to('F')
            yield "agec"
            fns.chord_to('D7')
            yield "d-cd"
            fns.chord_to('E7')
            yield "e-seE_De"
            fns.chord_to(fns.options('Am','F'))
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
    fns.choose_instruments(['rnd'])
    fns.chord_to(fns.options('F7','Fm7','D7'))
    if fns.chord == 'Fm7':
        yield "SDCo"
    else:
        yield "SDCa"
    yield "gsdc"
    fns.chord_to(fns.options('D7','Dm7','Gm7'))
    yield "a-_Acd-A"
    fns.chord_to(fns.options('Am7','Gm7'))
    #yield None

def gedc():
    fns.choose_instruments(['rnd'])
    if fns.coinflip():
        fns.chord_to(fns.options('Am','Am7','F','Fmaj7','Dm','Dm7','D7',))
    return 'AcdeA-A-'

def fedc():
    fns.choose_instruments(['rnd'])
    fns.chord = fns.options('Fm', 'Fm7', 'F minor major 7', 'Dm7b5', 'Bb7', 'Ab', 'Abmaj7')
    yield 'ogfgoC'
    
    # decide flat3
    if fns.sounding_chord in ('Fm7', 'Ab', 'Abmaj7'):
        flat3 = True
    elif fns.sounding_chord in ('F minor major 7',):
        flat3 = False
    else:
        flat3 = fns.options(True,False)
    
    if flat3:
        yield 'DSDoC--'
    else:
        yield 'DEDoC--'

def gbDEFESEG_EE_D__():
    fns.chord_to('Fmaj7')
    return 'E-CC--Cba-E-D-g-'

def abCD():
    chords = iter(fns.options(
        ('F','G','D','E','Am'),
        ('Dm','E','F','G','Am'),
        ('C','G','E7','E7','D7'),
    ))
    melody = iter(('E-EE','D-ED','Cb','ab','C-a-'))
    for melpart in melody:
        fns.chord_to(chords.next())
        yield melpart

def Cbag():
    fns.choose_instruments(['rnd'])
    fns.chord_to('D7')
    yield 'mEDC'
    fns.chord_to('G7')
    yield 'bagf'
    fns.chord_to('E7')
    yield 'eDCb'
    fns.chord_to('Am')
    yield 'a---'

def efede():
    dur = fns.options(.3,.25,.2,.15,.1)
    fns.change_duration(dur)

def edcAc_A():
    fns.chord_to('Am')
    return 'f--edcAAA'

def gagededc():
    fns.chord = 'Am'
    return '-cdceedc'

def aaaCb_a_():
    fns.chord_to('D7')
    return 'AAAcdeg-'

@fns.start_chord('Cm')
def gcccsd_c():
    fns.choose_instruments(['rnd'])
    fns.chord_to('Cm')
    yield '-cccsfgH'
    fns.chord_to('Bb')
    yield '-HHHdsfO'
    fns.chord_to('Ab')
    yield '-OOOcdsg'
    fns.chord_to('Fm')
    yield '-ogf-s-c'
    yield '-dsH-G--'

''' la bamba
@fns.start_chord('C')
def c_eg():
    fns.choose_instruments(['rnd'])
    fns.chord = 'F'
    yield 'f-a'
    fns.chord = 'G'
    yield 'g-_Bd'
    fns.chord = 'F'
    yield 'ffed'
    fns.chord = 'C'
    yield 'c-eg'
    fns.chord = 'F'
    yield 'f-a'
    fns.chord = 'G'
    yield 'g----'
    fns.chord = 'F'
    yield '----'
'''

def edcd():
    fns.choose_instruments(['rnd'])
    fns.chord = 'Am'
    yield 'e-dc'
    fns.chord = 'G'
    yield 'B-AG'
    fns.chord = 'F'
    yield 'FGAc'
    fns.chord = 'Em'
    yield 'B-AG'
    fns.chord = 'F'
    yield 'FGAc'
    fns.chord = 'G7'
    yield 'B-AG'
    fns.chord = 'C'
    yield 'cB'
    fns.chord = 'C7'
    yield 'cG'
    fns.chord = 'F'
    yield 'A---'


@fns.start_chord('Bm7b5')
@fns.start_dur(music.swung_dur(.4,.2).next)
def eses():
    fns.choose_instruments(['rnd'])
    fns.chord = 'E7'
    yield 'eged'
    fns.chord = 'Gm7'
    yield '-Hdf'
    fns.chord = 'Gm7'
    yield 'a-'
    fns.chord = 'C7'
    yield 'ge'
    fns.chord = 'Fmaj7'
    yield '-Ace'
    fns.chord = 'Fm7'
    yield 'g-'
    fns.chord = 'Bb7'
    yield 'fd'
    fns.chord = 'Ebmaj7'
    yield '--------'
    fns.DURATION = .2
    

if __name__ == '__main__':
    env = globals()
    #names = ('c_eg','edcd','fedc','eses')
    #env = fns.take_from_env(names, globals())
    fns.setup()
    fns.goof_around(env)
    fns.console(env = env)

