import midi, types, random, fns, pdb

def ceg():
    if fns.coinflip():
        response = fns.options(*"cdefgaBC")
    else:
        response = "dBG"
    if fns.coinflip():
        return gCgfe(response)
    else:
        return response

def edceg():
    return 'fed'

def gCgfe(gef=None, fde=None):
    if gef == "dBG":
        if fde == "cAG":
            return "ef|gCgfe"
        elif fde is 'fde':
            return "cAG";
        elif fde is None:
            return 'fde-cAG-';
    elif fde == "gafed":
        return "G-G-G---"
    elif (gef,fde) == ('d','e'):
        return 'c','A'
    else:
        return fns.options("c","G",
                        "cde","fed","Bcd","edc",
                        "egC","def","faD","efg",
                        "abC","baf","ede","eeA")

def edcHA():
    if fns.under_assumption('working with strings'):
        return 'fe-d'
    else:
        return ('f','e',None,'d')

def cefg():
    parts = ('fed-','cBA-')
    return fns.some_parts(*parts)

def cBA_():
    parts = ('fed-', 'cdefe')
    return fns.some_parts(*parts)

if __name__ == '__main__':
    fns.goof_around(globals())

