import sys
from music import fns as f

f.MEL_VEL = 127
f.CHORD_VEL = 80
f.INSTRUMENTS = (24, 49)
f.PAUSE_DISABLED = True

song_py_file = sys.argv[1]
execfile(song_py_file)
sys.argv = [] # blank out so inst setup doesn't get confused

if __name__=='__main__':
    f.setup()
    f.goof_around(globals())

