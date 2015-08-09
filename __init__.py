#!/usr/bin/python
# -*- coding: utf8 -*- 

'''
MIDI / Music Theory / Music Sequencing Fun in Python
====================================================
*by Ryan Murphy*

This python program sends MIDI notes to a MIDI interface to create music.

Environment / Dependencies
--------------------------

You need:

* python (I'm using python 2.7)
* rtmidi for sending midi messages - https://pypi.python.org/pypi/python-rtmidi
* a MIDI device capable of receiving MIDI messages and coverting them to sound

For example, my Mac couldn't play the MIDI file directly (at least I couldn't
figure out how), so I had to install a Synth / MIDI server called fluidsynth,
and start it up via e.g.:

    fluidsynth -d "/path/to/GeneralUser GS FluidSynth v1.44.sf2"

    in my case it's 
        fluidsynth -d "~/dev/GeneralUser GS 1.44 FluidSynth/GeneralUser GS FluidSynth v1.44.sf2"


Let's make some noise!
'''

#First we include some needed libraries:

#import pygame.midi
import rtmidi
import itertools, collections
import time
import random
from fractions import Fraction
from util2 import lispy_funcall, is_listy
import signal, sys


# midi.close() on KeyboardInterrupt
def close_midi_handler(signal, frame):
    #global midi
    #midi.close()
    global midiout
    del midiout
    sys.exit(0)

def install_close_handler():
    signal.signal(signal.SIGINT, close_midi_handler)

mel = [] # bank of melodies

def sleep(dur):
    dur = get_dur(dur)
    time.sleep(dur)

# I kept the option of a verbose `sleep()` function so that I could see the
# music outputted to the screen:

DURATION = .2
VELOCITY = 100

def verbose_sleep(dur):
    try: sleep.ticks
    except: sleep.ticks = 0
    if sleep.ticks % 64 == 0:
        print '------------------'
    elif sleep.ticks % 32 == 0:
        print '---------------'
    elif sleep.ticks % 16 == 0:
        print '------------'
    elif sleep.ticks % 8 == 0:
        print '---------'
    elif sleep.ticks % 4 == 0:
        print '------'
    else:
        print '---'
    sleep.ticks += 1
    dur = get_dur(dur)
    time.sleep(dur)

'''
So now if I wanted verbose timing output all I have to do is:
'''

# sleep = verbose_sleep


def verbose_sleep_6_8(dur):
    try: sleep.ticks
    except: sleep.ticks = 0
    if sleep.ticks % 48 == 0:
        print '------------------'
    elif sleep.ticks % 24 == 0:
        print '---------------'
    elif sleep.ticks % 12 == 0:
        print '------------'
    elif sleep.ticks % 6 == 0:
        print '---------'
    elif sleep.ticks % 2 == 0:
        print '------'
    else:
        print '---'
    sleep.ticks += 1
    dur = get_dur(dur)
    time.sleep(dur)

#sleep = verbose_sleep_6_8


'''
#todo #fixme - get rid of all the adhoc '-' comparisons, try to use do_hold_note
#todo #fixme - currently ',' and "'" will stop the last note, let it hold
'''

def midi_init():
    global midiout

    midiout = rtmidi.MidiOut()
    available_ports = midiout.get_ports()

    if available_ports:
        midiout.open_port(0)
    else:
        midiout.open_virtual_port("My virtual output")

    return midiout


midi_init()

#{

def is_special_val(pitch):
    return pitch in (None,'','-',',',"'")

def is_silent(pitch):
    if is_special_val(pitch):
        return True
    elif isinstance(pitch, Silent):
        return True
    else:
        return False

def do_hold_note(new_note): # decide whether to hold existing note
    return new_note in [None,'-',',',"'"]

'''
I created some low-level wrappers that turn a note
on or off using midi.note_on and midi.note_off.
'''

def midi_note_on(pitch, vel):
    control = [0x90, pitch, vel]
    midiout.send_message(control)

def midi_note_off(pitch):
    control = [0x80, pitch, 0]
    midiout.send_message(control)
    

'''
Now adding another layer that's a little more high-level.

The main changes I'm adding are just to shift the
pitches by a few octaves by default, and to tolerate
the value None (just don't do anything).
'''

def note_on(n, vel=VELOCITY, oct=4):
    '''print 'note_on', n, vel, oct'''      # -vv
    '''print n,'''                          # -v
    pitch = up(n, oct*12)
    if not is_silent(pitch):
        midi_note_on(pitch, vel)

def note_off(n, oct=4):
    pitch = up(n, oct*12)
    if not is_silent(pitch): # if the pitch was silent, no need to silence
        midi_note_off(pitch)

def note(n, dur=.2, vel=VELOCITY, oct=4):
    '''
    turn a note on, wait a specified duration, and then
    turn the note off:
    '''
    note_on(n, vel, oct)
    sleep(dur)
    note_off(n, oct)

def notes(ns, dur=.2, vel=VELOCITY, oct=4):
    playe(eventsg(ns, vel=vel, oct=oct, dur=dur))


def chord_on(ns, vel=VELOCITY, oct=4):
    for n in ns: note_on(n, vel, oct)

def chord_off(ns, oct=4):
    for n in ns: note_off(n, oct)


def chord(ns, dur=.2, vel=VELOCITY, oct=4):
    chord_on(ns, vel, oct)
    sleep(dur)
    chord_off(ns, oct)

'''
I became interested in having a more general function
that would turn a note or chord on.  If you provided just
a single note, it would turn the note on, but if you
provided a whole list/iterable, it would put all the
notes on as a chord:
'''

def notec_on(item, vel=VELOCITY, oct=4):
    if item in (None,''): return
    if isinstance(item,list) or isinstance(item,tuple):
        chord_on(item, vel, oct)
    else:
        note_on(item, vel, oct)

def notes_on_g(item, vel=VELOCITY, oct=4):
    if item in (None,''): yield None
    if isinstance(item,list) or isinstance(item,tuple):
        for note in item:
            yield ('note_on', note, vel, oct)
    else:
        yield ('note_on', item, vel, oct)

'''
And similarly, a `notec_off` function
that handles either a note or a whole chord:
'''

def notec_off(item, oct=4):
    if item in (None,''): return
    if isinstance(item,list) or isinstance(item,tuple):
        chord_off(item, oct)
    else:
        note_off(item, oct)

#}{

'''
Fun with Music Theory: adding Scales
------------------------------------

I added some different kinds of scales:
'''

scales = {
    'major' : [0,2,4,5,7,9,11],
    'lydian': [0,2,4,6,7,9,11],
    'minor' : [0,2,3,5,7,8,10],
    'dorian': [0,2,3,5,7,9,10],
    'harmonic minor': [0,2,3,5,7,8,11],
    'melodic minor' : [0,2,3,5,7,9,11],
}
chords = {
    'major': (0,4,7),
    'minor': (0,3,7),
    'diminished': (0,3,6),
    'diminished 7': (0,3,6,9),
    'major 7': (0,4,7,11),
    'minor 7': (0,3,7,10),
    'minor 6': (0,3,7,9),
    'minor major 7': (0,3,6,11),
    'half-diminished 7': (0,3,6,10),
}

'''
Then I made a function that would extend each scale
by adding several additional octaves
'''
def extend_scales(num_octs=4):
    for scale_type, scale in scales.items():
        scale += [n + 12*oct for oct in range(1,num_octs) for n in scale]
        scale += [scale[0]+12*num_octs]

'''
Now I wanted a function that would play up and down
all the scales, while printing out which ones they were:
'''
def play_scales(dur=.2):
    my_scales = random.sample(scales.keys(), 2)
    for scale_type in my_scales:
        scale = scales[scale_type]
        print scale_type
        for n in scale: note(n,dur=dur)            # ascending
        for n in scale[-2:0:-1] : note(n,dur=dur)  # descending
    note(scale[0], dur=2)

triad_scale_offsets = (0,2,4)

def scale_triad(scale, offs, invert=False):
    #todo #fixme - currently we 
    pat = triad_scale_offsets
    if invert: pat = tuple(-i for i in pat)
    return tuple(scale[offs + i] for i in pat)

def play_scale_triads(num_octs=2, dur=.2):
    for scale_type,scale in scales.items():
        print 'triads from the ' + scale_type + ' scale'
        # ascending
        for i in range(7*num_octs + 1):
            chord(scale_triad(scale, i), dur=dur)
        # descending
        for i in range(7*num_octs - 1, 0, -1):
            chord(scale_triad(scale, i), dur=dur)
    chord(scale_triad(scale, 0), dur=2)

def play_scale_triads_broken(num_octs=1, offs=7, dur=.2):
    for scale_type,scale in scales.items():
        print 'triads from the ' + scale_type + ' scale'
        # ascending
        for i in range(7*num_octs):
            notes(scale_triad(scale, i+offs), dur=dur)
        # descending
        for i in range(7*num_octs, -1, -1):
            notes(reversed(scale_triad(scale, i+offs)), dur=dur)
    chord(scale_triad(scale, 0), dur=2)

try:
    extend_scales()
    #play_scales()
    #play_scale_triads()
    #play_scale_triads_broken()
except KeyboardInterrupt:
    pass
finally:
    pass

#}{
#-- Tue Feb 24 2015 --

def up(pitch,amt): # transpose up
    if is_special_val(pitch): return pitch
    elif isinstance(pitch,list) or isinstance(pitch,collections.Iterable):
        return (up(p, amt) for p in pitch)
    else: return pitch + amt

def get_dur(dur):
    if dur is None:
        return DURATION
    elif callable(dur): # allow a function to be used for duration
        return dur()
    else:
        return dur

#deprecated, used notes()
'''
def play(notes_gen, dur=None):
    # notes_gen must be a generator that actually plays the notes with notec_on, notec_off etc
    for n in notes_gen:
        sleep(dur)
'''

play = notes

def swung_dur(long_dur=.4, short_dur=.2): #-- 06-01-15
    return icycle((long_dur, short_dur))

def swung_dur2(long_dur=.2, short_dur=.1):
    return icycle((long_dur, long_dur, short_dur, short_dur))

def play_swung(notes_gen):
    play(notes_gen, swung_dur().next) #todo #test, it said next() and I changed it

def rand(): # can be passed as duration for a random "wind chimes" effect
    amt = float(random.randint(1,50)) / 40
    return amt

#note play() leaves notes followed by '-' sounding for some reason.
    #todo allow play() to leave a note followed by '-' playing but then still turn it off when it's done

#todo make a function that takes an eventsg and filters out all the notes_off events
def remove_note_offs(events):
    for event in events:
        pass #todo




# with Rowan, allowed None to be passed to notec_on

cool_lick = iter([0,3,None,0,5,None,0,3,None,0,0,0,-2,0,0,0])
part2 = iter([3,7,None,3,9,None,9,7,None,3,5,7,None,5,3,None])
cool_lick_harm = iter([[0,3],[3,7],None,[0,3],[5,9],None,[0,9],[3,7],None,[0,3],[0,5],[0,7],-2,[0,5],[0,3],0])
cool_lick2 = [up(n,24) for n in[None,None,None,None,7,None,12,None,8,None,5,7,None,5,7,7]]

def play_cool_lick(dur=.2):
    cool_lick = [0,3,None,0,5,None,0,3,None,0,0,0,-2,0,0,0]*16
    play(cool_lick)

def play_cool_lick2_high(dur=.2):
    play(cool_lick2)



melody = itertools.cycle([1,2,3,4])
def play_1234_melody():
    play(melody)


def play_forever(lick_gen, dur=.2):
    play(itertools.cycle(lick_gen), dur=dur)


'''
cool_lick = iter([0,3,None,0,5,None,0,3,None,0,0,0,-2,0,0,0])
part2 = iter([3,7,None,3,9,None,9,7,None,3,5,7,None,5,3,None])
cool_lick_harm = iter([[0,3],[3,7],None,[0,3],[5,9],None,[0,9],[3,7],None,[0,3],[0,5],[0,7],-2,[0,5],[0,3],0])
'''

def combine(part1_gen,part2_gen):
    #todo #fixme: am I really using this or am I using izip?
        # lists don't work
        # xranges don't work either
    while True:
        x,y = (part1_gen.next(), part2_gen.next())
        if x is None or x is StopIteration:
            yield y
        elif y is None or y is StopIteration:
            yield x
        else:
            yield (x,y)
        if x is StopIteration and y is StopIteration:
            break

# example of combining parts and looping forever with a generator
part_i = iter([0,2,None,4,None,0,0,None,2])
part_j = iter([4,5,None,7,None,4,4,None,5])
ij4ever = itertools.izip(itertools.cycle(part_i), itertools.cycle(part_j))

izip = itertools.izip_longest
icycle = itertools.cycle

def sweet_groove():
   play_forever(izip(cool_lick, cool_lick2, part2)) 

#todo allow '-' to mean "hold previous pitches over"
#todo allow ' ' to mean "stop previous note"
#todo allow a Case Octave Shift to happen after a ' ': e.g. 'm-g-a-b-e-B-c-d---  B-emg-d-s-emgab---', the B should go Down


#}{
#-- Sun Mar 1 2015 --

# By simplifiying one aspect, can we learn new ways of adding complexity and excitement?
# e.g. if we've been using rich, complex, diverse chords to get excitement,
# can we simplify the chords and find that rich complex diversity in rhythm or melody or verse?

#-- Sun Mar 22 2015 --

# With Greyson last week, looking at music stuff, and trying an automated StartPage search
#   --> /Users/murftown/dev/repl-sessions/03-22-15:greyson-music-startpage.py.repl

#}{
#-- Mon Apr 6 2015 --

def two_hands(parts):
    return izip(parts['rh'],parts['lh'])

bach5bars = [
    {
        'rh': up([ '-','-', 3, 2,  3, '-',  5, '-',  7,'-','-','-',  8,'-','-','-' ],12),
        'lh':    [   3,'-',-9,'-','-','-', '-','-','-', 15, 14, 15, 12, 14, 10, 12 ],
    },
    {
        'rh': up([ '-','-', 5, 3,  5, '-',  7, '-',  8,'-','-','-',  10,'-','-','-' ],12),
        'lh':    [   8, 12,10,12,  8,  10,  7,   8,  5, 15, 14, 12, 14, 15, 12, 14 ],
    },
    {
        'rh': up([   7,'-',12,'-', 10,'-', 8,'-',  7, 8,10, 8, 7,'-', 5,'-' ],12),
        'lh':    [   3, 15,14, 12, 14, 15,12, 14, 10,15,14,12,10, 12, 8, 10 ],
    },
    {
        'rh': up([   3,'-', 7,'-', 10,'-', 15,'-','-', 12,14,15,17,'-',15,'-' ],12),
        'lh':    [   7, 12,10,  8,  7,  8,  5,  7,  0, 10, 9, 7, 9,  10, 7,  9 ],
    },
]
bach9bars = [
    { # Fm | Bbm
        'rh': up([  12, 10, 8, 7,  8, '-',  5,'-', 13,'-','-','-' ],12),
        'lh':    [  -7,'-', 5,'-','-',  7,  8,  7,  5,  3,  1,  0 ],
    },
    { # Gm7b5 | C7
        'rh': up([ '-', 12,10, 9,  10, '-', 7,'-', 16,'-','-','-' ],12),
        'lh':    [  -2,'-', 7,'-','-',  8, 10,  8,  7,  5,  4,  2 ],
    },
    { # C7
        'rh': up([ '-', 17,19,20, 22, '-',19, 16, 13,'-', 12,'-' ],12),
        'lh':    [   0,  2, 4, 5,  7,   8,10,  7,  5,  4,  5,  4 ],
    },
    { # Fm sus | Fm
        'rh': up([  10,  8,  7,  8,  10,13,12, 10, 8, 7, 5, 4 ],12),
        'lh':    [   5,'-','-','-', '-', 0, 2,  4, 5, 7, 8,10 ],
    },

    { # Fm | Bbm
        'rh': up([  -4,'-', 5,'-','-',  7,  8,  7,  5,  3,  1,  0 ],24),
        'lh':    [  12, 10, 8, 7,  8, '-',  5,'-', 13,'-','-','-' ],
    },
    { # Gm7b5 | C7
        'rh': up([  -2,'-', 7,'-','-',  8, 10,  8,  7,  5,  4,  2 ],24),
        'lh':    [ '-', 12,10, 9,  10, '-', 7,'-', 16,'-','-','-' ],
    },
    { # C7
        'rh': up([   0,  2, 4, 5,  7,   8,10,  7,  5,  4,  5,  4 ],24),
        'lh':    [ '-', 17,19,20, 22, '-',19, 16, 13,'-', 12,'-' ],
    },
    { # Fm sus | Fm
        'rh': up([   5,'-',  0, '-', '-', -2, -4, -5, -7,-8,-4,-5 ],24),
        'lh':    [  10,  8,  7,  8,   10, 13, 12, 10,  8, 7, 5, 4 ],
    },

    { # Fm
        'rh': up([  12, 10,8,  7,   8,'-', 5,'-', 20, '-','-','-'],12),
        'lh':    [   8,'-',5,'-', '-',  7, 8,  7,  5,   3,  1,  0],
    },
    { # Bo7
        'rh': up([  '-', 19,17, 16,  17,'-',14,'-', 11,'-','-','-'],12),
        'lh':    [   -1,'-', 8,'-', '-',  7, 5,  3,  2,  0, -1, -3],
    },
    { # G7
        'rh': up([  '-',12,14,15, 17,'-',14,11, 8,'-',7,'-'],12),
        'lh':    [   -5,-3,-1, 0,  2,  3, 5, 2, 0, -1,0, -1],
    },
    { # Cm
        'rh': up([  '-',  5, 3,  2,   3,'-', 0,'-', 15,'-','-','-'],12),
        'lh':    [    3,'-',12,'-', '-', 14,15, 14, 12, 10,  9,  7],
    },
]
'''
    { # F#o7
        'rh': up([],12),
        'lh':    [],
    },
    { # D7
        'rh': up([],12),
        'lh':    [],
    },
    { # G7 | Cm
        'rh': up([],12),
        'lh':    [],
    },
    { # Fm | G7
        'rh': up([],12),
        'lh':    [],
    },
    { # Cm | Fm
        'rh': up([],12),
        'lh':    [],
    },
    { # Dm7b5 | G7
        'rh': up([],12),
        'lh':    [],
    },
    { # G7
        'rh': up([],12),
        'lh':    [],
    },
    { # Cm sus | Cm
        'rh': up([],12),
        'lh':    [],
    },
    { # F7
        'rh': up([],12),
        'lh':    [],
    },
    { # Bbm
        'rh': up([],12),
        'lh':    [],
    },
'''

def consolidate_bars(both_hands_bars):
    return {
        'rh': list(itertools.chain(*[b['rh'] for b in both_hands_bars])),
        'lh': list(itertools.chain(*[b['lh'] for b in both_hands_bars])),
    }
    

def play_piece(piece):
    play(two_hands(consolidate_bars(piece)))

# e.g. play_piece(bach9bars) - #todo #fixme - this seems to note hold out '-' notes

#}{
#-- Sun May 3 2015 --

note_name_str = 'crdsefmgoahbCRDSEFMGOAHB'
note_names = {k:v for k,v in enumerate(note_name_str)}
note_numbers = {v:k for k,v in note_names.items()}

note_names[None] = ' '
note_numbers[' '] = None
# reflexive keys: these are all "themselves"
note_names['-'] = '-' # hold prev note
note_numbers['-'] = '-'
note_names['_'] = '_' # play note down an octave from prev
note_numbers['_'] = '_'
note_names[','] = ',' # silently go down an octave
note_numbers[','] = ','
note_names["'"] = "'" # silently go up an octave
note_numbers["'"] = "'"

'''
with open(bach4,'r') as fh:
    bach4str = fh.read()
'''


#-- Sun May 31 2015 --

def note_diff(note1,note2):
    #print 'note_diff({note1},{note2})'.format(note1=note1,note2=note2)
    if note1 == None or note2 == None \
             or note1 == '-' or note2 == '-':
        #print '  returning None'
        return None
    else:
        #print '  returning ', (note2-note1)
        return note2-note1

def abs_note_diff(note1,note2):
    diff = note_diff(note1,note2)
    if diff is not None:
        return abs(diff)
    else:
        return None

BIG_OFFSET = 12

def subtract_24_til_close_enough(prev, n):
    #print ' subtract_24_til_close_enough(', prev, n, ')'
    while note_diff(prev,n) > BIG_OFFSET:
        n -= 24
        #print ' -= 24 =', n
    #print ' returning', n
    return n
def add_24_til_close_enough(prev, n):
    #print ' add_24_til_close_enough(', prev, n, ')'
    while note_diff(prev,n) <= -BIG_OFFSET:
        n += 24
        #print ' += 24 =', n
    #print ' returning', n
    return n

def int_or_self(x): # int() won't allow param None, nor can return it
    if isinstance(x, object) and hasattr(x, '__int__'):
        return int(x)
    else:
        return x

class Silent(object):
    '''used to allow "'" and "," to go up and down an octave without making a sound'''
    def __init__(self, note):
        self.note = int(note) # don't let note be itself a Silent()
    def __repr__(self):
        val = repr(self.note)
        return 'Silent(' + val + ')'
    def __int__(self):
        return self.note
    def __add__(self, i):
        return Silent(int(self) + int(i))
    def __radd__(self, i):
        return self.__add__(i)
    def __sub__(self, i):
        return Silent(int(self) - int(i))
    def __rsub__(self, i):
        return Silent(int(i) - int(self))
    def __abs__(self):
        return Silent(abs(int(self)))
    def __neg__(self): # unary -
        return Silent(-int(self))
    def __cmp__(self, i):
        return cmp(int_or_self(self), int_or_self(i))
    def __rcmp__(self, i):
        return cmp(int_or_self(i), int_or_self(self))

def close_big_intervals(nums):
    '''
    change octaves to close up any gaps bigger than say an octave
    used by strn2pitches to allow the octave-wrapping letter case semantics
    '''
    prev = None
    for n in nums:
        if n == '_': # "_" goes down an octave
            n = prev - 12
        elif n == ',': # silently go down an octave
            n = Silent(prev - 12)
        elif n == "'": # silently go up an octave
            n = Silent(prev + 12)
        else: # figure out what octave to play the next note
            diff = abs_note_diff(prev,n)
            if diff >= BIG_OFFSET:
                #todo #fixme - this following comparison has weird values in it sometimes like None and ''!  seems to work tho
                if n > prev: # going up?
                    n = subtract_24_til_close_enough(prev, n) # go down instead
                else: # going down?
                    n = add_24_til_close_enough(prev, n) # go up instead
        yield n
        if n not in ['-',' ']: prev = n

def strn2numbers(strn):
    return (note_numbers[ch] for ch in strn)

def strn2pitches(strn):
    return close_big_intervals(strn2numbers(strn))

def play_strn(strn, dur=DURATION):
    notes(strn2pitches(strn), dur=dur)

#-- Mon Jun 1 2015 --

def wind_chimes():
    while True:
        strn = raw_input('> ')
        play_strn(strn, rand)

nostalgic_arp_melody = 'cdefgegCECEGcGcedAFAFDaDafdfdAFA'
nostalgic_accomp     = 'e-e--egfe-e--egef-d---A---D---  '
mel.append(nostalgic_arp_melody)

def play_nostalgic_arp_melody():
    play_strn(nostalgic_arp_melody * 2)
    play_strns([nostalgic_arp_melody * 2, nostalgic_accomp], octs=[0,2])




# Bach Invention 4 in Dm
bach4strn = [
    "defgahrhagfef-a-D-g-R-E-DEFGAHRHAGFEFDEFGAhAGFEDECDEFGaGFEDCDEFDEFg-----CDECDEf---h---a-g-Chagfefgagfgf-C-C-CDCDCDCDCDCDCDCDCDChagfeCdemgahagfedhcdefgabCDEFoFEDCbCbDCbaoaomedcdemoadCbaomemoabCmEDCbaoabCDEaFEDCbAOMEA--EC-baa--ahCdChagahgahCDeDChaga-FEF-g-E-  DEFGAHRHAGFEF-D-g--DREaRDbR--DDChagfh-rdefgaDf-edd-----------",
    "------------defgahrhagfef-a-D-e-g-R-d-D-f-g-a-h-c-C-e-f-g-a-hgahCDeDChagafgahCdChagfecdefgAgfedcdHc-_-FGAHcdEdcHAGAHcdefGfedcHAHcAHcM-----GAHGAHE-----F-f-d-B-O-E-AOABcdefefefefefefefefefefefefefefefe-E-D-C-b-a-D-E-F-D-E-_-a_HcdsMsdcHAG--GAHC-G-c-fgabRDeDRbagf-a-D-e-g-R-defgahrhagfefga-_-H--cHAG'hagfefga-_-D-----------",
]
bach6strn = [
    "  E---S---D---R---b---a---o---m---oao-bab-omo-ese---m---o---a---b---R---S---E-S-R-b-E---_-------'-O---E---R---ESE-R-h-m---M---S---b---SRS-b-o-e---E---R---h---O---M---E---S---R---b-h-ese-hoh-bhb-s-r-b-r-h-b-----b-S-M-B-----B-M-S-b-m-s-B-----"*2,
    "e---m---o---a---b---R---S---E-S-R-b-E---_---------e---s---d---r---B---A---O---M---OAO-BAB-OMO-ESE---r---e---m---h---R-,-S---B---s---e---o---b-,-R---r---e---m---o---h---b---e---o---m-R-h-R-e-R-s---e---m---B-bhb-mem-srs-mem-srs-BHB-----,-b-'-"*2,
]

def play_strns(strns, octaves=None, dur=None, vel=VELOCITY):
    parts = [strn2pitches(s) for s in strns]
    if octaves: # transpose as needed
        for i,part in enumerate(parts):
            parts[i] = up(parts[i], octaves[i]*12)
    combined = izip(*parts)
    notes(combined, dur=dur, vel=vel)

def play2hands(strns, octaves=(1,0), dur=None):
    play_strns(strns, octaves=octaves, dur=dur)

def play_bach4(octaves=(1,0), dur=None, vel=VELOCITY):
    play2hands(bach4strn, dur=dur)

def play_bach6(dur=None):
    play2hands(bach6strn, dur=dur)

#}{

# -- Wed Jun 3 2015 --

# look at the last_note or all the last_notes
# as well as the current_note or all the current_notes
# and decide which notes to turn off
def notes_off_g(sounding_notes, new_notes, oct):
    if isinstance(sounding_notes, collections.Iterable):
        for i,note in enumerate(sounding_notes):
            corresponding_new_note = None
            if isinstance(new_notes, collections.Iterable):
                new_notes = list(new_notes) # in case it's a generator
                if len(new_notes) > i:
                    corresponding_new_note = new_notes[i]

            stop_this_note = False
            #if corresponding_new_note not in [None,'-']:
            if not do_hold_note(corresponding_new_note):
                stop_this_note = True
            elif new_notes is None:
                stop_this_note = True
            elif new_notes == '-':
                stop_this_note = False

            if note != '-' and stop_this_note:
                yield ('note_off', note, oct)
    else: # single last note
        if new_notes != '-':
            yield ('note_off', sounding_notes, oct)


def iterable(x):
    return isinstance(x, collections.Iterable)


def show_list_spatially(positions, held_positions=None, offset=0):
    dim, undim = '\033[2m', '\033[0m'
    max_width = 80
    chars = [' '] * max_width
    if held_positions:
        for pos in held_positions:
            if isinstance(pos, int):
                adjusted_pos = pos + offset
                if 0 <= adjusted_pos < max_width:
                    chars[adjusted_pos] = dim + '|' + undim
    for pos in positions:
        if isinstance(pos, int):
            adjusted_pos = pos + offset
            if 0 <= adjusted_pos < max_width:
                chars[adjusted_pos] = '●'
    strn = ''.join(chars)
    return strn

iter_type = type(iter([0]))

def eventsg(ns, dur=.2, vel=VELOCITY, oct=4, sounding_notes = None, leave_sounding = False):
    'this generator, treats note on and note off as separate events, and has sleep events in between'
    #note: this works pretty well! needs some cleanup
        #todo there's an issue where if one voice runs out of notes before the other
        # it will leave the last note hanging.  None should stop the voice

    first_time = True
    for n in ns:
        if isinstance(n, iter_type):
            new_notes = list(n)
        elif not is_listy(n):
            new_notes = [n]
        else:
            new_notes = n

        if not first_time:
            these_note_offs = []
            for this_note_off in notes_off_g(sounding_notes, new_notes, oct):
                these_note_offs.append(this_note_off[1])
                yield this_note_off
            #if len(these_note_offs): print "off:", these_note_offs,

        first_time = False
        
        # note_on - #todo make a generator that does this one at a time instead of notec_on
        these_note_ons = []
        for this_note_on in notes_on_g(new_notes, vel, oct):
            note = this_note_on[1]
            if note != '-':
                these_note_ons.append(note)
                yield this_note_on
        #if len(these_note_ons): print "on:", these_note_ons

        # update sounding notes
        if isinstance(new_notes, collections.Iterable):
            if not isinstance(sounding_notes, collections.Iterable):
                sounding_notes = new_notes
            else:
                sounding_notes = list(sounding_notes)
                for i,nn in enumerate(new_notes):
                    if nn is not '-':
                        if len(sounding_notes) > i:
                            sounding_notes[i] = nn
                        else:
                            sounding_notes.append(nn)
        elif new_notes is not '-':
            sounding_notes = new_notes

        print show_list_spatially(new_notes, sounding_notes, offset=30)

        # sleep
        yield ('sleep', dur)

        
    # if we actually played any notes...
    if not first_time and not leave_sounding:
        # note off's for last note
        for this_note_off in notes_off_g(sounding_notes, n, oct):
            yield this_note_off


def playe(events):
    for e in events:
        #if len(e) and e[0] != 'sleep': print str(e)
        lispy_funcall(e, env=globals())

#}{
#-- Fri Jun 5 2015 --

'''
whoa, generators tripping me out!

trying to figure out how sending and receiving works
'''

'''
#todo figure out how to allow me to type chars in vim and have it play notes
def yield_me():
    i = 0
    while True:
        x = (yield i)
        yield x
        i += 1

feed_me_chars = []
def read_slowly_from_chars():
    global feed_me_chars
    ptr = 0
    while True:
        print 'loop'
        print feed_me_chars, ptr
        if len(feed_me_chars) > ptr:
            print ' more!'
            note_char = feed_me_chars[ptr]
            print ' yield!'
            yield note_char
            print ' ptr++'
            ptr += 1
        else:
            sleep(.1)
ReadSlowly = read_slowly_from_chars()
'''



#}{

#-- Mon Jun 8 2015 --

chorales = {
    'bach': {
        47: [
            'a-a-f-g-a-f-e-d-----  ',
            'f-e-d-r-def-r-A-----  ',
            'D-a-a-g-D_D-a-f-----  ',
            'd-r-d-e-fga-_-d-----  ',
        ],
        49: [
            'd---a---a---g---D---C---b---a-------    C---b---a---b-------a-------    b---C---b---C---a---g-f-e---d-------    a---a---g---f-e-d---c-------    a---f---C---a---g-f-g---a-------    g---f-e-d---c---f---e-d---r-d-------------------',
            'a---D---F---E---M-O-A-----O-E-------    A-----O-A---F---E-D-C-------    G---G---G---G---F---E-D-R---a-------    E-D-E-R-D-E-a---h---a-------    E---D---C-G---F-E-D-R-D-E-------    E---D-C-b---a-b-R-D-E-F-G-------M-E-M-----------',
            'f-g-a---D-C-b---a-b-C-DEF-E-C-------    E---F-EDCba---Dbo---a-------    D---E---D---C-----D-R-D-a-g-f-------    a---g-f---e-f-------f-------    a---a---g---C-D-E-F-E-D-R-------    a---a-g-f---e---a-----------h---a-g-a-----------',
            'd-e-f-e-f-d-e-d-c-B-A-c-d-e-A-------    a---d-e-f-e-d-B-e---A-------    g-f-e-f-g-f-e-c-f-d-h-g-a---d-------    r-B-r-A-B-r-d-c-d-e-f-------    r---d---e---f---g-a-h---a-------    r---d---O---A-----B-r-d-A---D-------------------',
        ],
        54: [
            'g-D-D-D-D-E-DCb-    a-bRD-E-E-D-------  D-D-D-D-bCD-Cba---  D-C-b-a-a-gabCD---  D-C-bab-a-g--------',
            'd-dem-g-g-g-m-g-    a-g-m-emg-m-------  a-g-m-g-g-g-agm---  m-ga-ggem-g---m---  g-g-g-g-m-d--------',
            'b-a-DCbCD-CbaDD-    D-g-a-b-R-a-------  DCb-C-D-E-D-E-a---  b-babCD-C-b-E-D---  b-CDE-D-DCb--------',
            'g-m-d-gab-c-d-g-    m-e-d-g-a-d-------  m-g-a-b-e-B-c-d-----B-emg-d-s-emgab---  g-e-dcd-d-G--------',
        ],
        55: [
            'bRD-R-b---  '*2+'M-E-D-R---  R-D-D-E-E-M-M-E-D-R---b---  M-E-D-R---  M-E-D-R---  R-D-D-E-E-M-M-E-D-R---b---',
            'm-b-h-m---  '*2+'mga-m-m---  m-m-m-b-a-a-abR-m-m--ed---  b-bhb-h---  bao-aba---  a-agm-bao-R-bhb-b-b-h-m---',
            'DEM-MED---  '*2+'abR-b-h---  h-bRD-D-R-D-D-R-b-b-h-m---  D-E-M-M---  M-b-MEE---  E-MEDRb-E-E-DRbRDEM--ES---',
            'b-B-M-D---  '*2+'D-A-B-M---  M-B-BAGEAGMEDRbhb-m---b---  b-R-DEM---  D-E-MOA---  AGM-BAO-rBH-d-OHB-M---b---',
        ],
    },

    'ryan': {
        0: [
            'e-f-g-fed-e-f--ge-----  g-C-bag-m-b---',
            'c--Bc-A-A-c-c-B-c-----  e-a-e-e-b-b---      esemgeagmes--ee---  ',
            'g-gfe-fga-f-d-g-g-----  g-e-c-b-A-G---',
            'c-G-c---f-d-g-_-c-----  c-M---E-S-E-------E--MG-B-c-A-M-B-E---  ',
        ],
    }
}

def play_chorale(num=None, composer=None, dur=.5, vel=VELOCITY):
    global chorales
    if composer is None:
        unique_composers = chorales.keys()
        weighted_composers = []
        for composer in unique_composers:
            num_chorales = len(chorales[composer])
            weighted_composers.extend([composer] * num_chorales)
        composer = random.choice(weighted_composers)
    if num is None:
        nums = chorales[composer].keys()
        num = random.choice(nums)
    chorale = chorales[composer][num]
    octaves = (1,1,0,0)
    if num == 49: octaves = (1,0,0,0)
    elif num == 55: octaves = (1,1,0,-1)
    play_strns(chorale, octaves = octaves, dur=dur, vel=vel)

def test():
    play([0,2,4]) 

#-- Sat Jun 13 2015 --

# got ' and , to work!

#play_bach4()

chordtxt = {
    'C major': 'ceg',
    'Db major': 'rfo',
    'D major': 'dma',
    'Eb major': 'sgh',
    'E major': 'eob',
    'F major': 'faC',
    'F# major': 'mhR',
    'G major': 'gbD',
    'Ab major': 'oCS',
    'A major': 'aRE',
    'Bb major': 'hDF',
    'B major': 'bSM',

    'C major 7': 'cegb',
    'Db major 7': 'rfoC',
    'D major 7': 'dmaR',
    'Eb major 7': 'sghD',
    'E major 7': 'eobS',
    'F major 7': 'faCE',
    'F# major 7': 'mhRF',
    'G major 7': 'gbDM',
    'Ab major 7': 'oCSG',
    'A major 7': 'aREO',
    'Bb major 7': 'hDFA',
    'B major 7': 'bSMH',

    'C minor': 'csg',
    'Db minor': 'reo',
    'D minor': 'dfa',
    'Eb minor': 'smh',
    'E minor': 'egb',
    'F minor': 'foC',
    'F# minor': 'maR',
    'G minor': 'ghD',
    'Ab minor': 'obS',
    'A minor': 'aCE',
    'Bb minor': 'hRF',
    'B minor': 'bDM',

    'C minor 7': 'csgh',
    'Db minor 7': 'reob',
    'D minor 7': 'dfaC',
    'Eb minor 7': 'smhR',
    'E minor 7': 'egbD',
    'F minor 7': 'foCS',
    'F# minor 7': 'maRE',
    'G minor 7': 'ghDF',
    'Ab minor 7': 'obSM',
    'A minor 7': 'aCEG',
    'Bb minor 7': 'hRFO',
    'B minor 7': 'bDMA',

    'C half-diminished 7': 'csmh',
    'Db half-diminished 7': 'regb',
    'D half-diminished 7': 'dfoC',
    'Eb half-diminished 7': 'smaR',
    'E half-diminished 7': 'eghD',
    'F half-diminished 7': 'fobS',
    'F# half-diminished 7': 'maCE',
    'G half-diminished 7': 'ghRF',
    'Ab half-diminished 7': 'obDM',
    'A half-diminished 7': 'aCSG',
    'Bb half-diminished 7': 'hREO',
    'B half-diminished 7': 'bDFA',

    'C diminished': 'csm',
    'Db diminished': 'reg',
    'D diminished': 'dfo',
    'Eb diminished': 'sma',
    'E diminished': 'egh',
    'F diminished': 'fob',
    'F# diminished': 'maC',
    'G diminished': 'ghR',
    'Ab diminished': 'obD',
    'A diminished': 'aCS',
    'Bb diminished': 'hRE',
    'B diminished': 'bDF',

    'C diminished 7': 'csma',
    'Db diminished 7': 'regh',
    'D diminished 7': 'dfob',
    'Eb diminished 7': 'smaC',
    'E diminished 7': 'eghR',
    'F diminished 7': 'fobD',
    'F# diminished 7': 'maCS',
    'G diminished 7': 'ghRE',
    'Ab diminished 7': 'obDF',
    'A diminished 7': 'aCSM',
    'Bb diminished 7': 'hREG',
    'B diminished 7': 'bDFO',

    'C augmented': 'ceo',
    'Db augmented': 'rfa',
    'D augmented': 'dmh',
    'Eb augmented': 'sgb',
    'E augmented': 'eoC',
    'F augmented': 'faR',
    'F# augmented': 'mhD',
    'G augmented': 'gbS',
    'Ab augmented': 'oCE',
    'A augmented': 'aRF',
    'Bb augmented': 'hDM',
    'B augmented': 'bSG',
}

def is_pure_chord(pitches, root, chord_quality):
    chord_pitches = up(chords[chord_quality], root)
    chord = list(get_pitch_classes(chord_pitches))
    for pitch in pitches:
        pc = pitch_class(pitch)
        print pc
        if pc in chord:
            print 'in'
        else:
            print 'not in'
            return False
    return True



home_dir = '/Users/murftown/'
with open(home_dir + 'git1/songs/when today becomes tomorrow') as fh:
    when_today_becomes_tomorrow = fh.read() \
        .replace('\n','')




# #todo chord detection (unfinished)
# given a set of pitches, figure out if it is all notes of a certain chord
c_maj_arp = [0,4,7,12,16,12,7,4,0]
Eb_maj_arp = [3,7,10,15,19,15,10,7,3]

def pitch_class(pitch):
    return pitch % 12

def get_pitch_classes(pitches):
    # give back the same format you get (list vs generator etc)
    if isinstance(pitches, list):
        return [pitch_class(p) for p in pitches]
    elif isinstance(pitches, tuple):
        return tuple(pitch_class(p) for p in pitches)
    else: # generator
        return (pitch_class(p) for p in pitches)

def subtract_min(pitches):
    pitches = tuple(pitches) # in case it's a generator, solidify it
    min_p = min(pitches)
    # give back the same format you get (list vs generator etc)
    return tuple(p - min_p for p in pitches)

def try_roots(pitch_classes):
    'try each of the pitch_classes as if they were the root'
    pitch_classes = tuple(pitch_classes) # in case it's a generator, solidify it
    uniq_pitch_classes = set(pitch_classes)
    for possible_root in uniq_pitch_classes:
        this_try = tuple(p - possible_root for p in pitch_classes)
        yield possible_root, get_pitch_classes(this_try) # re-normalize negatives

def detect_pure_chord_prenormalized(normalized_pitches):
    uniq_pitches = set(normalized_pitches)
    for chord_type, chord_pitches in chords.items():
        if set(chord_pitches) == uniq_pitches:
            return chord_type

def detect_pure_chord(pitches):
    tries = try_roots(get_pitch_classes(pitches))
    for root, normalized_pitches in tries:
        chord_type = detect_pure_chord_prenormalized(normalized_pitches)
        if chord_type:
            return root, chord_type

def detect_pure_chord_strn(mus_strn):
    pitches = strn2pitches(mus_strn)
    chordinfo = detect_pure_chord(pitches)
    if chordinfo:
        root, chord_type = chordinfo
        root = note_names[root]
        return root, chord_type


def play_something():
    r = random.randint(0,4)
    if r == 0:
        play_bach4()
    elif r == 1:
        sweet_groove()
    elif r == 2:
        play_scale_triads_broken()
    elif r == 3:
        play_nostalgic_arp_melody()
    elif r == 4:
        r = random.randint(0,1)
        if r == 0:
            play_chorale()
        else:
            play_chorale(dur=swung_dur(.4,.2).next)
    elif r == 5:
        play_strn(when_today_becomes_tomorrow)

if __name__ == '__main__':
    if random.randint(0,1)==0:
        play_something()

