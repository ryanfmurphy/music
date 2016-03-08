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

import rtmidi
import itertools, collections
import time
import random
from fractions import Fraction
from util2 import lispy_funcall, is_listy
import signal, sys
from pprint import pprint as pp
import copy


def close_midi_handler(signal, frame):
    global midiout
    del midiout
    sys.exit(0)

def install_close_handler():
    signal.signal(signal.SIGINT, close_midi_handler)

def sleep(dur):
    NOTE_DISPLAYER.show_accumulated_notes()
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
        print('------------------')
    elif sleep.ticks % 32 == 0:
        print('---------------')
    elif sleep.ticks % 16 == 0:
        print('------------')
    elif sleep.ticks % 8 == 0:
        print('---------')
    elif sleep.ticks % 4 == 0:
        print('------')
    else:
        print('---')
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
        print('------------------')
    elif sleep.ticks % 24 == 0:
        print('---------------')
    elif sleep.ticks % 12 == 0:
        print('------------')
    elif sleep.ticks % 6 == 0:
        print('---------')
    elif sleep.ticks % 2 == 0:
        print('------')
    else:
        print('---')
    sleep.ticks += 1
    dur = get_dur(dur)
    time.sleep(dur)

#sleep = verbose_sleep_6_8


'''
#todo #fixme - get rid of all the adhoc '-' comparisons, try to use do_hold_note
#todo #fixme - currently ',' and "'" will stop the last note, let it hold

#todo do some stuff with the Russian Doll chord concept - C -> Am -> F -> Dm etc
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


'''low-level midi message functionality'''

def midi_note_on(pitch, vel, chan=0):
    control = [0x90 + chan, pitch, vel]
    midiout.send_message(control)

def midi_note_off(pitch, chan=0):
    control = [0x80 + chan, pitch, 0]
    midiout.send_message(control)

def midi_panic():
    for i in range(127):
        for ch in range(16):
            midi_note_off(i, chan=ch) 

def midi_program_change(instrument_no, chan=0):
    control = [0xc0 + chan, instrument_no]
    midiout.send_message(control)

panic = midi_panic
prog_chg = midi_program_change


'higher level functionality - octave offset & some rest / note holding logic'



class NoteDisplayer:

    def __init__(self):
        self.notes = set()
        self.prev_notes = set()

    #todo accumulate positions before you print a line of notes
    #   (allowing multiple zipped events generators to be properly displayed
    def start_note(self, note_pos):
        self.notes.add(note_pos)
        # allow rearticulation by not considering it a "held note"
        # (remove from prev_notes)
        self.prev_notes.discard(note_pos)

    def release_note(self, note_pos):
        self.notes.discard(note_pos)

    def show_accumulated_notes(self):
        #todo do I really need the list() conversion?
        held_notes = self.prev_notes.intersection(self.notes)
        notes = list(
            self.notes - held_notes
        )
        #print('notes',self.notes) 
        #print('prev',self.prev_notes) 
        #print('held',held_notes) 
        print(
            show_list_spatially(notes, list(held_notes))
        )
        self.prev_notes = self.notes
        self.notes = copy.copy(self.notes)



SHOW_NOTES = True
SHOW_NOTE_NAMES = True
NOTE_DISPLAYER = NoteDisplayer()

def note_on(n, vel=VELOCITY, oct=4, chan=0,
            show_notes=SHOW_NOTES, show_note_names=SHOW_NOTE_NAMES):
    pitch = up(n, oct*12)
    if not is_silent(pitch):
        midi_note_on(pitch, vel, chan=chan)
    if show_notes:
        NOTE_DISPLAYER.start_note(pitch)

def note_off(n, oct=4, chan=0,
             show_notes=SHOW_NOTES, show_note_names=SHOW_NOTE_NAMES):
    pitch = up(n, oct*12)
    if not is_silent(pitch): # if the pitch was silent, no need to silence
        midi_note_off(pitch, chan=chan)
    if show_notes:
        NOTE_DISPLAYER.release_note(pitch)

def rand_inst(chan=0):
    instrument = random.randint(0,127)
    midi_program_change(instrument, chan=chan)
    return instrument


def play(ns, dur=DURATION, vel=VELOCITY, oct=4, leave_sounding=False, chan=0):
    if dur is None: dur = DURATION
    playe(eventsg(ns, vel=vel, oct=oct, dur=dur, leave_sounding=leave_sounding, chan=chan))


def chord_on(ns, vel=VELOCITY, oct=4, chan=0):
    if ns:
        for n in ns:
            note_on(n, vel, oct, chan=chan)

def chord_off(ns, oct=4, chan=0):
    if ns:
        for n in ns:
            note_off(n, oct, chan=chan)

def chordstrn_on(chordstrn, vel=VELOCITY, oct=4, chan=0):
    if chordstrn:
        pitches = strn2pitches(chordstrn)
        chord_on(pitches, vel=vel, oct=oct, chan=chan)

def chordstrn_off(chordstrn, oct=4, chan=0):
    if chordstrn:
        pitches = strn2pitches(chordstrn)
        chord_off(pitches, oct=oct, chan=chan)

def chordname_on(chordname, vel=VELOCITY, oct=4, chan=0):
    if chordname:
        if chordname in chordtxt:
            chordstrn = chordtxt[chordname]
            chordstrn_on(chordstrn, vel=vel, oct=oct, chan=chan)

def chordname_off(chordname, oct=4, chan=0):
    if chordname:
        if chordname in chordtxt:
            chordstrn = chordtxt[chordname]
            chordstrn_off(chordstrn, oct=oct, chan=chan)


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

def notec_on(item, vel=VELOCITY, oct=4, chan=0):
    if item in (None,''): return
    if isinstance(item,list) or isinstance(item,tuple):
        chord_on(item, vel, oct, chan=chan)
    else:
        note_on(item, vel, oct, chan=chan)

def notes_on_g(item, vel=VELOCITY, oct=4, chan=0):
    if item in (None,''): yield None
    if isinstance(item,list) or isinstance(item,tuple):
        for note in item:
            yield ('note_on', note, vel, oct, chan)
    else:
        yield ('note_on', item, vel, oct, chan)

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

def get_scale(scale_type_or_scale):
    if isinstance(scale_type_or_scale, str):
        return scales[scale_type_or_scale]
    else:
        return scale_type_or_scale


'scale ascending and descending'

def eventsg_scale(scale, dur=DURATION, omit_last=False, leave_sounding=False):
    'scale can be a scale_type or a scale itself'
    scale = get_scale(scale)
    'ascending'
    for e in eventsg(scale, dur=dur, leave_sounding=leave_sounding):
        yield e
    'descending'
    if omit_last:
        desc_scale = scale[-2:0:-1]
    else:
        desc_scale = scale[-2::-1]
    for e in eventsg(desc_scale, dur=dur, leave_sounding=leave_sounding):
        yield e

def play_scale(scale, dur=DURATION, omit_last=False):
    playe(
        eventsg_scale(scale, dur, omit_last)
    )

def choose_some_scales():
    return random.sample(scales.keys(), 2)

def play_scales(dur=DURATION):
    my_scales = choose_some_scales()
    for i,scale_type in enumerate(my_scales):
        print(scale_type)
        is_last = True if i == len(my_scales) - 1 else False
        omit_last = False if is_last else True
        play_scale(scale_type, omit_last=omit_last)

triad_scale_offsets = (0,2,4)

def scale_triad(scale, offs, invert=False):
    pat = triad_scale_offsets
    if invert: pat = tuple(-i for i in pat)
    return tuple(scale[offs + i] for i in pat)

def scale_triads(scale, num_octs=2, omit_last=False):
    scale = get_scale(scale)
    'ascending'
    ascending_range = range(7*num_octs + 1)
    for i in ascending_range:
        yield scale_triad(scale, i)
    'descending'
    if omit_last: descending_range = range(7*num_octs - 1, 0, -1)
    else:         descending_range = range(7*num_octs - 1, -1, -1)
    for i in descending_range:
        yield scale_triad(scale, i)

def play_scales_triads(num_octs=2, dur=.2, leave_sounding=True):
    my_scales = choose_some_scales()
    for i,scale_type in enumerate(my_scales):
        print('triads from the ' + scale_type + ' scale')
        is_last = True if i == len(my_scales) - 1 else False
        omit_last = False if is_last else True
        play(
            scale_triads(scale_type, num_octs, omit_last=omit_last),
            leave_sounding=leave_sounding
        )

def scale_broken_triads(scale, num_octs=1, offs=7, dur=DURATION):
    scale = get_scale(scale)
    # ascending
    for i in range(7*num_octs):
        for j in scale_triad(scale, i+offs):
            yield j
    # descending
    for i in range(7*num_octs, -1, -1):
        for j in reversed(scale_triad(scale, i+offs)):
            yield j

def play_scales_broken_triads(num_octs=1, offs=7, dur=DURATION):
    for scale_type,scale in scales.items():
        print('triads from the ' + scale_type + ' scale')
        play(
            scale_broken_triads(scale_type, num_octs=num_octs, offs=offs, dur=dur),
            leave_sounding=False
        )
    chord(scale_triad(scale, 0), dur=2)

def init_music_theory():
    extend_scales()

init_music_theory()

'-- Tue Feb 24 2015 --'

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

'''
* #todo make a function that takes an eventsg and filters out all the notes_off events
'''
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
ichain = itertools.chain.from_iterable
lchain = lambda x: list(ichain(x))
dbl = lambda L: lchain([i,i] for i in L)

def sweet_groove():
   play_forever(izip(cool_lick, cool_lick2, part2)) 

#todo allow '-' to mean "hold previous pitches over"
#todo allow ' ' to mean "stop previous note"
#todo allow a Case Octave Shift to happen after a ' ': e.g. 'm-g-a-b-e-B-c-d---  B-emg-d-s-emgab---', the B should go Down


'-- Mon Apr 6 2015 --'

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

'-- Sun May 3 2015 --'

note_name_str = 'crdsefmgoahbCRDSEFMGOAHB'
note_names = {k:v for k,v in enumerate(note_name_str)}

note_numbers = {
    'c':0, 'i':0,
    'j':1, 'r':1,
    'd':2, 'y':2, 'z':2,
    'k':3, 's':3,
    'e':4, 't':4,
    'f':5, 'l':5,
    'm':6, 'u':6,
    'g':7, 'v':7,
    'o':8, 'n':8,
    'a':9, 'w':9, 'x':9,
    'h':10, 'p':10,
    'b':11, 'q':11,
    'C':12, 'I':12,
    'J':13, 'R':13,
    'D':14, 'D':14, 'Y':14, 'Z':14,
    'S':15, 'K':15,
    'E':16, 'T':16,
    'F':17, 'L':17,
    'M':18, 'U':18,
    'G':19, 'V':19,
    'O':20, 'N':20,
    'A':21, 'W':21, 'X':21,
    'H':22, 'P':22,
    'Q':23, 'B':23,
}

#note_numbers = {v:k for k,v in note_names.items()}
#note_names = {v:k for k,v in note_numbers.items()}

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

def note_name(pitch_num):
    if pitch_num is None:
        return ' '
    else:
        return note_names[pitch_num % 24]


'-- Sun May 31 2015 --'

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


def close_1_big_interval(n, prev):
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
    return n


def close_big_intervals(nums, prev_pitch=None):
    '''
    change octaves to close up any gaps bigger than say an octave
    used by strn2pitches to allow the octave-wrapping letter case semantics
    '''
    for n in nums:
        n = close_1_big_interval(n, prev_pitch)
        yield n
        if n not in ['-',' ',None]: prev_pitch = n


def close_big_intervals_interactive(prev_pitch = None):
    'just like close_big_intervals but you have to .send it the nums and you instantly get the next yield'
    n = None
    while True:
        n = yield n
        if n is None: return
        n = close_1_big_interval(n, prev_pitch)
        #todo #fixme should this next line be above?
        if n not in ['-',' ']: prev_pitch = n

def strn2numbers(strn):
    return (note_numbers[ch] for ch in strn)

def strn2pitches(strn, prev_pitch=None):
    return close_big_intervals(strn2numbers(strn), prev_pitch)

def eventsg_strn(strn, dur=DURATION, leave_sounding=False,
                 show_notes=None, prev_pitch=None,
                 vel=VELOCITY, oct=4):
    global SHOW_NOTES
    if show_notes is None: show_notes = SHOW_NOTES
    return eventsg(
        strn2pitches(strn, prev_pitch),
        dur=dur, vel=vel, oct=oct,
        leave_sounding=leave_sounding,
        show_notes=show_notes,
    )

def play_strn(strn, dur=DURATION, leave_sounding=False,
              show_notes=None, prev_pitch=None,
              vel=VELOCITY):
    global SHOW_NOTES
    if show_notes is None: show_notes = SHOW_NOTES
    if strn is None:
        return None
    else:
        # playe returns the last pitch for continuity with subsequent melodies
        return playe(
            eventsg_strn(strn,
                         dur=dur,
                         leave_sounding=leave_sounding,
                         show_notes=show_notes,
                         prev_pitch=prev_pitch,
                         vel=vel,
            )
        )

estrn = eventsg_strn
pstrn = play_strn


def strn_note_on(ch):
    pitch = note_numbers[ch]
    note_on(pitch)    

'-- Mon Jun 1 2015 --'

def wind_chimes():
    while True:
        strn = raw_input('> ')
        play_strn(strn, rand)

nostalgic_arp_melody = 'cdefgegCECEGcGcedAFAFDaDafdfdAFA'
nostalgic_accomp     = 'e-e--egfe-e--egef-d---A---D---  '

def play_nostalgic_arp_melody():
    play_strn(nostalgic_arp_melody * 2)
    play_strns([nostalgic_arp_melody * 2, nostalgic_accomp], octaves=[0,2])

# Bach Invention 4 in Dm
bach4strn = [
    "defgahrhagfef-a-D-g-R-E-DEFGAHRHAGFEFDEFGAhAGFEDECDEFGaGFEDCDEFDEFg-----CDECDEf---h---a-g-Chagfefgagfgf-C-C-CDCDCDCDCDCDCDCDCDChagfeCdemgahagfedhcdefgabCDEFoFEDCbCbDCbaoaomedcdemoadCbaomemoabCmEDCbaoabCDEaFEDCbAOMEA--EC-baa--ahCdChagahgahCDeDChaga-FEF-g-E-  DEFGAHRHAGFEF-D-g--DREaRDbR--DDChagfh-rdefgaDf-edd-----------",
    "------------defgahrhagfef-a-D-e-g-R-d-D-f-g-a-h-c-C-e-f-g-a-hgahCDeDChagafgahCdChagfecdefgAgfedcdHc-_-FGAHcdEdcHAGAHcdefGfedcHAHcAHcM-----GAHGAHE-----F-f-d-B-O-E-AOABcdefefefefefefefefefefefefefefefe-E-D-C-b-a-D-E-F-D-E-_-a_HcdsMsdcHAG--GAHC-G-c-fgabRDeDRbagf-a-D-e-g-R-defgahrhagfefga-_-H--cHAG'hagfefga-_-D-----------",
]
bach6strn = [
    "  E---S---D---R---b---a---o---m---oao-bab-omo-ese---m---o---a---b---R---S---E-S-R-b-E---_-------'-O---E---R---ESE-R-h-m---M---S---b---SRS-b-o-e---E---R---h---O---M---E---S---R---b-h-ese-hoh-bhb-s-r-b-r-h-b-----b-S-M-B-----B-M-S-b-m-s-B-----"*2,
    "e---m---o---a---b---R---S---E-S-R-b-E---_---------e---s---d---r---B---A---O---M---OAO-BAB-OMO-ESE---r---e---m---h---R-,-S---B---s---e---o---b-,-R---r---e---m---o---h---b---e---o---m-R-h-R-e-R-s---e---m---B-bhb-mem-srs-mem-srs-BHB-----,-b-'-"*2,
]

# Q. How does this compare to using zip_events later?
def eventsg_parts(parts, octaves=None, dur=DURATION,
                  vel=VELOCITY, show_notes=None):
    global SHOW_NOTES
    if show_notes is None: show_notes = SHOW_NOTES
    if octaves: # transpose as needed
        for i,part in enumerate(parts):
            parts[i] = up(parts[i], octaves[i]*12)
    combined = izip(*parts)
    for e in eventsg(combined, dur=dur, vel=vel,
                     show_notes=show_notes):
        yield e

def eventsg_strns(strns, octaves=None, dur=DURATION,
                  vel=VELOCITY, show_notes=None):
    global SHOW_NOTES
    if show_notes is None: show_notes = SHOW_NOTES
    parts = [strn2pitches(s) for s in strns]
    for e in eventsg_parts(parts, octaves=octaves, dur=dur,
                           vel=vel, show_notes=show_notes):
        yield e

def play_strns(strns, octaves=None, dur=None, vel=VELOCITY):
    playe(eventsg_strns(strns, octaves=octaves, dur=dur, vel=vel))


def play_whatever(thing, show_notes=None):
    global SHOW_NOTES
    if show_notes is None: show_notes = SHOW_NOTES
    err = ValueError('Unknown thing ' + thing + ' given to play_whatever()')
    if isinstance(thing, str):
        play_strn(thing, show_notes=show_notes)
    elif is_listy(thing) and len(thing) > 0:
        if isinstance(thing[0], str):
            play_strns(thing, show_notes=show_notes)
        elif isinstance(thing[0], int):
            play(thing, show_notes=show_notes)
        else:
            raise err
    else:
        raise err

def play2hands(strns, octaves=(1,0), dur=None):
    play_strns(strns, octaves=octaves, dur=dur)

def play_bach4(octaves=(1,0), dur=None, vel=VELOCITY): #specific
    play2hands(bach4strn, dur=dur)

def play_bach6(dur=None): #specific
    play2hands(bach6strn, dur=dur)


'-- Wed Jun 3 2015 --'

'''
look at the last_note or all the last_notes
as well as the current_note or all the current_notes
and decide which notes to turn off
'''
def notes_off_g(sounding_notes, oct, chan=0, new_notes=None):
    if isinstance(sounding_notes, collections.Iterable):
        for i,note in enumerate(sounding_notes):
            corresponding_new_note = None
            if isinstance(new_notes, collections.Iterable):
                new_notes = list(new_notes) # in case it's a generator
                if len(new_notes) > i:
                    corresponding_new_note = new_notes[i]

            stop_this_note = False
            if corresponding_new_note:
                if do_hold_note(corresponding_new_note):
                    stop_this_note = False
                else:
                    stop_this_note = True
            else:
                if new_notes is None: # don't hold any notes
                    stop_this_note = True
                elif new_notes == '-': # hold all notes
                    stop_this_note = False
                else: # new, #test 
                    stop_this_note = True

            if note != '-' and stop_this_note: #todo maybe use do_hold_note() instead? not sure
                yield ('note_off', note, oct)
    else: # single last note
        #if new_notes != '-':
        if do_hold_note(new_note): #test
            yield ('note_off', sounding_notes, oct, chan)


def iterable(x):
    return isinstance(x, collections.Iterable)




def show_list_spatially(positions, held_positions=None, offset=0, show_note_names=False):
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
                if show_note_names:
                    chars[adjusted_pos] = note_name(pos)
                else:
                    chars[adjusted_pos] = '●'
    strn = ''.join(chars)
    return strn

iter_type = type(iter([0]))

def eventsg(ns, dur=DURATION, vel=VELOCITY, oct=4, chan=0,
            sounding_notes = None, leave_sounding = False,
            show_notes = None, show_note_names = True #todo remove show_*
           ):

    'this generator, treats note on and note off as separate events, and has sleep events in between'

    '#note: this eventsg works pretty well! needs some cleanup'

    "#todo there's an issue where if one voice runs out of notes before the other\
    it will leave the last note hanging.  Passing 'None' should stop the voice"

    global SHOW_NOTES
    if show_notes is None: show_notes = SHOW_NOTES
    if dur is None: dur = DURATION

    first_time = True
    for n in ns:
        if isinstance(n, iter_type):
            new_notes = list(n)
        elif not is_listy(n):
            new_notes = [n]
        else:
            new_notes = n

        #print "sounding notes:", sounding_notes
        #print "whereas new notes:", new_notes
        if not first_time:
            these_note_offs = []
            for this_note_off in notes_off_g(sounding_notes, oct, chan, new_notes):
                #print '  an off:',this_note_off
                these_note_offs.append(this_note_off[1])
                yield this_note_off
            #if len(these_note_offs): print "off:", these_note_offs,

        first_time = False
        
        # note_on - #todo make a generator that does this one at a time instead of notec_on
        these_note_ons = []
        for this_note_on in notes_on_g(new_notes, vel, oct, chan=chan):
            note = this_note_on[1]
            if note != '-':
                these_note_ons.append(note)
                yield this_note_on
        #if len(these_note_ons): print "on:", these_note_ons

        # update sounding notes - #todo simplify! why do all this when we already figured out the note offs?
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
                if len(new_notes) < len(sounding_notes):
                    sounding_notes = sounding_notes[:len(new_notes)]
        elif new_notes is not '-':
            sounding_notes = new_notes

        #if show_notes:
            #print(show_list_spatially(new_notes, sounding_notes, offset=30, show_note_names=show_note_names))

        # sleep
        yield ('sleep', dur)

        
    # if we actually played any notes...
    if not first_time and not leave_sounding:
        # note off's for last note
        for this_note_off in notes_off_g(sounding_notes, oct, chan):
            yield this_note_off


def playe(events, silence_on_abort = False):
    if silence_on_abort:
        try:
            return playe(events, silence_on_abort = False)
        except KeyboardInterrupt:
            panic()
    else:
        last_pitch = None
        for e in events:
            # get pitch from last note_on event
            possible_pitch = get_lispy_funcall_pitch(e)
            if possible_pitch is not None: last_pitch = possible_pitch
            # exec actual funcall
            lispy_funcall(e, env=globals())
        return last_pitch

def get_lispy_funcall_pitch(e):
    if e[0] == 'note_on':
        return e[1]

'-- Fri Jun 5 2015 --'

# whoa, generators tripping me out!
# trying to figure out how sending and receiving works

##todo figure out how to allow me to type chars in vim and have it play notes
#def yield_me():
#    i = 0
#    while True:
#        x = (yield i)
#        yield x
#        i += 1
#
#feed_me_chars = []
#def read_slowly_from_chars():
#    global feed_me_chars
#    ptr = 0
#    while True:
#        print('loop')
#        print(feed_me_chars, ptr)
#        if len(feed_me_chars) > ptr:
#            print(' more!')
#            note_char = feed_me_chars[ptr]
#            print(' yield!')
#            yield note_char
#            print(' ptr++')
#            ptr += 1
#        else:
#            sleep(.1)
#ReadSlowly = read_slowly_from_chars()



'-- Mon Jun 8 2015 --'

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
            'e-f-g-fed-e-f--ge-----  g-C-bag-m-b-----  g--medcBA-c-B-A-G-----  e-f-g-fed-e-f--ge-----  g-C-bag-m-b-----  g--medcBA-c-B-A-O-----  ',
            'c--Bc-A-d-c-c-B-c-----  e-a-e-e-a-g-----    esemgeagmes--ee-----  c--Bc-A-d-c-c-B-c-----  e-a-e-e-a-g-----    esemgeagmes--ee-----  ',
            'g-gfe-fga-f-d-g-g-----  g-e-c-b-b-b-------b-----e-m-b---C-b-----  g-gfe-fga-f-d-g-g-----  g-e-c-b-b-b-------b-----e-m-b---C-b-----  ',
            'c-G-c---f-d-g-_-c-----  c-M---E-S-E-------E--MG-B-c-A-M-B-E-----  c-G-c---f-d-g-_-c-----  c-M---E-S-E-------E--MG-B-c-A-M-B-E-----  ',
        ],
    },

    'evan': {
        0: [
            'c-BcdcB-ABcBA-G-c-_-----',
            'efgfe-d-d-c-B-A-G-B-c---',
            'g---a-b-bagefgf-g-e-----',
            'c---e-g---e-d-g-_-c-----',
        ],
    }
}

'instruments I like (fluidR3 soundfont) ->'
cool_instruments = {
    0: 'piano',
    44: 'strings',
    68: 'woodwinds',
    70: 'bassoon', # goes well with 44 strings
    73: 'flute',
    87: 'spiky pad',
}
cool_inst_combos = (
    (24,  49), # guitar and strings (#nice #balance)
    (70,  44), # bassoon and strings (#nice #balance)
    (25,  76), # twangy guitar thing and pad (#todo #balance pad could be a bit louder)
    (61,  73), # brass lead with tremolo woodwind pad
    (36, 104), # twangy lead with brassy pad
    (36,  73), # twangy lead with tremolo woodwind pad
    (10,  63), # bells and brassy pad
    ( 0,   0), # piano and piano
)
def cool_inst_combo():
    return random.choice(cool_inst_combos)

def play_chorale(num=None, composer=None, dur=.5, vel=VELOCITY):
    global chorales

    'choose a chorale if not provided'
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

    'setup'
    chorale = chorales[composer][num]
    octaves = (1,1,0,0)
    if composer == 'bach':
        if num == 49: octaves = (1,0,0,0)
        elif num == 55: octaves = (1,1,0,-1)
    elif composer == 'evan':
        if num == 0: octaves = (2,1,0,0)

    'play it'
    play_strns(chorale, octaves = octaves, dur=dur, vel=vel)

def test():
    play([0,2,4]) 

'-- Sat Jun 13 2015 --'

"#done - got ' and , to work!"

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

    # short for major
    'C': 'ceg',
    'Db': 'rfo',
    'D': 'dma',
    'Eb': 'sgh',
    'E': 'eob',
    'F': 'faC',
    'F#': 'mhR',
    'G': 'gbD',
    'Ab': 'oCS',
    'A': 'aRE',
    'Bb': 'hDF',
    'B': 'bSM',

    'C7': 'cegh',
    'Db7': 'rfob',
    'D7': 'dmaC',
    'Eb7': 'sghR',
    'E7': 'eobD',
    'F7': 'faCS',
    'F#7': 'mhRE',
    'G7': 'gbDF',
    'Ab7': 'oCSM',
    'A7': 'aREG',
    'Bb7': 'hDFO',
    'B7': 'bSMA',

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

    'C major 6': 'cega',
    'Db major 6': 'rfoh',
    'D major 6': 'dmab',
    'Eb major 6': 'sghC',
    'E major 6': 'eobR',
    'F major 6': 'faCD',
    'F# major 6': 'mhRS',
    'G major 6': 'gbDE',
    'Ab major 6': 'oCSF',
    'A major 6': 'aREM',
    'Bb major 6': 'hDFG',
    'B major 6': 'bSMO',

    'Cmaj7': 'cegb',
    'Dbmaj7': 'rfoC',
    'Dmaj7': 'dmaR',
    'Ebmaj7': 'sghD',
    'Emaj7': 'eobS',
    'Fmaj7': 'faCE',
    'F#maj7': 'mhRF',
    'Gmaj7': 'gbDM',
    'Abmaj7': 'oCSG',
    'Amaj7': 'aREO',
    'Bbmaj7': 'hDFA',
    'Bmaj7': 'bSMH',

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

    'Cm': 'csg',
    'Dbm': 'reo',
    'Dm': 'dfa',
    'Ebm': 'smh',
    'Em': 'egb',
    'Fm': 'foC',
    'F#m': 'maR',
    'Gm': 'ghD',
    'Abm': 'obS',
    'Am': 'aCE',
    'Bbm': 'hRF',
    'Bm': 'bDM',

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

    'Cm7': 'csgh',
    'Dbm7': 'reob',
    'Dm7': 'dfaC',
    'Ebm7': 'smhR',
    'Em7': 'egbD',
    'Fm7': 'foCS',
    'F#m7': 'maRE',
    'Gm7': 'ghDF',
    'Abm7': 'obSM',
    'Am7': 'aCEG',
    'Bbm7': 'hRFO',
    'Bm7': 'bDMA',

    'C minor 6': 'csga',
    'Db minor 6': 'reoh',
    'D minor 6': 'dfab',
    'Eb minor 6': 'smhC',
    'E minor 6': 'egbR',
    'F minor 6': 'foCD',
    'F# minor 6': 'maRS',
    'G minor 6': 'ghDE',
    'Ab minor 6': 'obSF',
    'A minor 6': 'aCEM',
    'Bb minor 6': 'hRFG',
    'B minor 6': 'bDMO',

    'Cm6': 'csga',
    'Dbm6': 'reoh',
    'Dm6': 'dfab',
    'Ebm6': 'smhC',
    'Em6': 'egbR',
    'Fm6': 'foCD',
    'F#m6': 'maRS',
    'Gm6': 'ghDE',
    'Abm6': 'obSF',
    'Am6': 'aCEM',
    'Bbm6': 'hRFG',
    'Bm6': 'bDMO',

    'C minor major 7': 'csgb',
    'Db minor major 7': 'reoC',
    'D minor major 7': 'dfaR',
    'Eb minor major 7': 'smhD',
    'E minor major 7': 'egbS',
    'F minor major 7': 'foCE',
    'F# minor major 7': 'maRF',
    'G minor major 7': 'ghDM',
    'Ab minor major 7': 'obSG',
    'A minor major 7': 'aCEO',
    'Bb minor major 7': 'hRFA',
    'B minor major 7': 'bDMH',

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

    'Cm7b5': 'csmh',
    'Dbm7b5': 'regb',
    'Dm7b5': 'dfoC',
    'Ebm7b5': 'smaR',
    'Em7b5': 'eghD',
    'Fm7b5': 'fobS',
    'F#m7b5': 'maCE',
    'Gm7b5': 'ghRF',
    'Abm7b5': 'obDM',
    'Am7b5': 'aCSG',
    'Bbm7b5': 'hREO',
    'Bm7b5': 'bDFA',

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

    'Co': 'csm',
    'Dbo': 'reg',
    'Do': 'dfo',
    'Ebo': 'sma',
    'Eo': 'egh',
    'Fo': 'fob',
    'F#o': 'maC',
    'Go': 'ghR',
    'Abo': 'obD',
    'Ao': 'aCS',
    'Bbo': 'hRE',
    'Bo': 'bDF',

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

    'Co7': 'csma',
    'Dbo7': 'regh',
    'Do7': 'dfob',
    'Ebo7': 'smaC',
    'Eo7': 'eghR',
    'Fo7': 'fobD',
    'F#o7': 'maCS',
    'Go7': 'ghRE',
    'Abo7': 'obDF',
    'Ao7': 'aCSM',
    'Bbo7': 'hREG',
    'Bo7': 'bDFO',

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

    'C+': 'ceo',
    'Db+': 'rfa',
    'D+': 'dmh',
    'Eb+': 'sgb',
    'E+': 'eoC',
    'F+': 'faR',
    'F#+': 'mhD',
    'G+': 'gbS',
    'Ab+': 'oCE',
    'A+': 'aRF',
    'Bb+': 'hDM',
    'B+': 'bSG',

    'Csus': 'cfg',
    'Dbsus': 'rmo',
    'Dsus': 'dga',
    'Ebsus': 'soh',
    'Esus': 'eab',
    'Fsus': 'fhC',
    'F#sus': 'mbR',
    'Gsus': 'gCD',
    'Absus': 'oRS',
    'Asus': 'aDE',
    'Bbsus': 'hSF',
    'Bsus': 'bEM',

    'C lydian': 'cemg',
    'Db lydian': 'rfgo',
    'D lydian': 'dmoa',
    'Eb lydian': 'sgah',
    'E lydian': 'eohb',
    'F lydian': 'fabC',
    'F# lydian': 'mhCR',
    'G lydian': 'gbRD',
    'Ab lydian': 'oCDS',
    'A lydian': 'aRSE',
    'Bb lydian': 'hDEF',
    'B lydian': 'bSFM',

    'Clyd': 'cemg',
    'Dblyd': 'rfgo',
    'Dlyd': 'dmoa',
    'Eblyd': 'sgah',
    'Elyd': 'eohb',
    'Flyd': 'fabC',
    'F#lyd': 'mhCR',
    'Glyd': 'gbRD',
    'Ablyd': 'oCDS',
    'Alyd': 'aRSE',
    'Bblyd': 'hDEF',
    'Blyd': 'bSFM',
}

chord_progressions = [
    ['C major', 'F major', 'G major', 'C major'],
    ['F major', 'F major', 'C major', 'C major', 'Bb major', 'Bb major', 'F major', 'F major'],
    ['C minor', 'C minor', 'Bb major', 'Bb major', 'Eb major', 'Eb major', 'C minor', 'C minor'],
    ['G minor 7', 'A minor 7', 'Bb major 7'],
    # All of Me
    dbl(['C major', 'E7', 'A7', 'D minor',
    'E7', 'A minor', 'D7', 'G7',
    'C major', 'E7', 'A7', 'D minor'])
        + ['F major', 'F minor', 'E minor 7', 'A7',
        'D minor 7', 'G7', 'C major', 'C major'],
    # My Funny Valentine
    [
    'C minor', 'C minor major 7', 'C minor 7', 'C minor 6',
    'Ab major 7', 'F minor 7', 'D half-diminished 7', 'G7'
    ],
    dbl([ 'Am', 'Dm', 'G', ]) + ['C','E7'],
]

all_of_me = chord_progressions[3]
my_funny_valentine = chord_progressions[4]

def coinflip():
    return random.randint(1,2) == 1

def play_all_of_me():
    playe(all_of_me_e())

def all_of_me_e():
    if coinflip():
        return eventsg_cp(all_of_me, pattern=[0,2,1,2]*2, dur=swung_dur(.4,.2).next)
    else:
        return eventsg_cp(all_of_me, oct_pattern=[(0,0),(2,0),([0,1],0),(2,0),(0,1),([0,1],0),(2,0),(0,1)])

def play_valentine():
    playe(valentine_e())

def valentine_e():
    return eventsg_cp(my_funny_valentine, pattern=[0,1,2,3]*2, dur=swung_dur(.4,.2).next)

def play_cp(chord_progression, times=1, pattern=None, oct_pattern=None, dur=None):
    playe(
        eventsg_cp(chord_progression, times=times, pattern=pattern, oct_pattern=oct_pattern, dur=dur)
    )

def expand_chord(chord, pattern=None, oct_pattern=None):
    'returns numeric pitches of chord, optionally applying a pattern or oct_pattern'
    if pattern:
        return strn2pitches(apply_pattern(pattern, chordtxt[chord]))
    elif oct_pattern:
        cp_pitches = strn2pitches(chordtxt[chord])
        return apply_oct_pattern(oct_pattern, cp_pitches)
    else:
        return strn2pitches(chordtxt[chord])

def eventsg_cp(chord_progression, times=1, pattern=None, oct_pattern=None, dur=None):
    for i in range(times):
        for chord in chord_progression:
            pitches = expand_chord(chord, pattern=pattern, oct_pattern=oct_pattern)
            for event in eventsg(pitches, dur=dur):
                yield event

def apply_pattern(idx_pattern, bank):
    return (bank[i] for i in idx_pattern)

#todo extend pattern across octaves with a generator so it doesn't matter if some chords don't have enough notes in chord
def apply_oct_pattern(idx_oct_pattern, bank):
    'this time the pattern has (idx,oct) tuples'
    "can't be used directly on strings, need pitch numbers"

    bank = list(bank); "in case it's a generator"
    def get1pitch(idx,oct):
        if isinstance(idx,int):
            return bank[idx] + 12*oct
        else: # collection of idx's
            return [get1pitch(i,oct) for i in idx]
    return (get1pitch(i,oct) for i,oct in idx_oct_pattern)

def is_pure_chord(pitches, root, chord_quality):
    chord_pitches = up(chords[chord_quality], root)
    chord = list(get_pitch_classes(chord_pitches))
    for pitch in pitches:
        pc = pitch_class(pitch)
        print(pc)
        if pc in chord:
            print('in')
        else:
            print('not in')
            return False
    return True



'''
home_dir = '/Users/murftown/'
with open(home_dir + 'git1/songs/when today becomes tomorrow') as fh:
    when_today_becomes_tomorrow = fh.read() \
        .replace('\n','')
'''




'chord detection - given a set of pitches, figure out if it is all notes of a certain chord'

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



'create a improvized accompaniment of randomized chords'

def random_groovy_chord(mode=None):
    if mode is None: mode = random.randint(0,3)
    if mode == 0:
        chords = ('G minor 7', 'A minor 7', 'Bb major 7'); 'a groovy classic option'
    elif mode == 1:
        chords = ('G minor 7', 'A minor 7', 'Bb major 7', 'F major 7', 'Eb major 7', 'D minor 7')
    elif mode == 2:
        chords = chordtxt.keys(); 'all chords'
    elif mode == 3:
        chords = ('F major 7', 'D7', 'Esus', 'G major 7', 'Ab major 7')
    else:
        raise ValueError('mode {mode} out of range'.format(mode=mode))
    chord = random.choice(chords)
    print(chord)
    return strn2pitches(chordtxt[chord])

def play_random_groovy_chord(modo=False):
    chord_on(random_groovy_chord(modo))

def random_groovy_chords(mode=None):
    while True:
        chord = list(random_groovy_chord(mode)); 'solidify generator'
        times = 1 #random.randint(1,2)
        for n in range(times):
            yield chord
            dur = random.randint(2,6)
            sleep(dur)

def play_random_groovy_chords(mode=None, vel=VELOCITY):
    try:
        last_chord = None
        for chord in random_groovy_chords(mode):
            chord = list(chord); 'solidify generator'
            chord_off(last_chord)
            chord_on(chord, vel=vel)
            last_chord = chord
    except KeyboardInterrupt:
        chord_off(last_chord)
        

rgc = play_random_groovy_chords
def rgci(*args, **kwargs):
    rand_inst()
    rgc(*args, **kwargs)




def play_something():
    'play something - anything!'
    r = random.randint(0,6)
    if r == 0:
        play_bach4()
    elif r == 1:
        sweet_groove()
    elif r == 2:
        r2 = random.randint(0,2)
        if r2 == 0:
            play_scales()
        elif r2 == 1:
            play_scales_triads()
        elif r2 == 2:
            play_scales_broken_triads()
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
    elif r == 6:
        play_random_groovy_chords()



'drum track'

DRUM_CHAN = 9
KICK, SNARE, HH = -12, -10, -6

drum_beats = [
    [KICK,KICK,(HH,KICK),KICK,SNARE,None,(HH,KICK),KICK,None,KICK,HH,KICK,SNARE,None,HH,None],
    [KICK,None,HH,None,SNARE,None,HH,KICK,None,KICK,(KICK,HH),None,SNARE,None,HH,SNARE],
]


def play_drums(dur=DURATION, vel=VELOCITY):
    beat = random.choice(drum_beats)
    while True:
        playe(eventsg(beat, chan=DRUM_CHAN, vel=vel), silence_on_abort=False)
    #drum_loop_events = icycle(eventsg(beat, chan=DRUM_CHAN, vel=vel))
    #playe(drum_loop_events)





def zip_events(*event_streams):
    'combine 2 event streams, splitting the "sleep" commands if needed to give each event its proper timing'
    stream_done = [False for i in event_streams]
    next_event = [None for i in event_streams]

    while True:

        still_finding_nonsleep_events = True

        while still_finding_nonsleep_events:

            still_finding_nonsleep_events = False; "until proven True"

            for i, event_stream in enumerate(event_streams):
                'if needed, get event from this event_stream if any'
                if next_event[i] is None and not stream_done[i]:
                    try:
                        next_event[i] = event_stream.next()
                    except StopIteration:
                        stream_done[i] = True

                'go through all non-sleep events with no hesitation'
                if next_event[i] is not None and not is_sleep_event(next_event[i]):
                    yield next_event[i]
                    still_finding_nonsleep_events = True
                    next_event[i] = None

        "now everything's either a sleep or it's done"
        'deal with sleep events now that all event streams are either sleeping or StopIteration'
        sleep_events = [event for event in next_event if is_sleep_event(event)]
        if len(sleep_events) == 0: break
        min_sleep_amt = min(get_sleep_time(event) for event in sleep_events)
        yield ('sleep', min_sleep_amt); 'do the minimum sleep'

        'subtract that minimum sleep amt from all the other sleeps'
        for i,event in enumerate(next_event):
            if event is None:
                pass
            elif get_sleep_time(event) == min_sleep_amt:
                next_event[i] = None
            else: # we have bigger sleep, subtract the small sleep (replace event)
                current_sleep_time = get_sleep_time(next_event[i])
                next_event[i] = ('sleep', current_sleep_time - min_sleep_amt)

zipe = zip_events

def playz(*event_streams):
    return playe(zip_events(*event_streams))
        

def is_sleep_event(event):
    return isinstance(event, tuple) and len(event) and event[0]=='sleep'

def get_sleep_time(event):
    if is_sleep_event(event):
        return event[1]
    else:
        return None

def open_chord(pitches):
    'move 1 or more internal voices up an octave to open the voicing'
    pitches = list(sorted(pitches))
    if len(pitches) in (3,4):
        pitches[1] += 12 # raise an octave
        return list(sorted(pitches))
    else:
        return None # couldn't do anything

def try_open_chord(pitches):
    "open chord if there's an option to, but return the chord regardless"
    open1 = open_chord(pitches)
    if open1:
        return open1
    else:
        return pitches


'maybe play something if invoked directly instead of imported'

if __name__ == '__main__':
    if random.randint(0,1)==0:
        play_something()

