from __future__ import print_function
import midi
from isness import *
import types, random, code, ast, _ast, readline, sys, os, atexit
from strict_typing import types as typerule

MEL_VEL = 110
CHORD_VEL = 95
RESPONSE_OFFSET = 30
DURATION = .2 #music.swung_dur(.4,.2).next
SOMETIMES_DELAY = True
PAUSE_DISABLED = True
INSTRUMENTS = None
SHOW_NOTES = True
midi.SHOW_NOTE_NAMES = False
VERBOSE = False

chord = None
sounding_chord = None

def log(*args):
    if VERBOSE:
        print(*args)

# change the chord to the_chord only if it's not already
@typerule(the_chord=str)
def chord_to(the_chord):
    global chord, sounding_chord
    if the_chord != sounding_chord:
        chord = the_chord

@typerule(assumption=str)
def under_assumption(assumption):
    if assumption == 'working with strings':
        return True
    else:
        return False

def options(*things):
    return random.choice(things)

@typerule(env=dict, _ret_type=dict)
def get_funcs(env):
    return {k:v for k,v in env.items()
            if is_function(v)}

def play_funcs(env):
    if is_module(env):
        env = env.__dict__
    funcs = get_funcs(env).items()
    random.shuffle(funcs)
    for func_name,func in funcs:
        if coinflip():
            times = 1
        else:
            times = options(1,2,4)
        for x in range(times):
            play_func(func)
        maybe_delay()

def maybe_delay():
    return midi.playe(ev_maybe_delay())

def ev_maybe_delay():
    if SOMETIMES_DELAY and coinflip(2):
        delay_len = options(8,16,24,32) #,48,64)
        log('.' * delay_len)
        delay = '-' * delay_len
        for e in midi.ev_strn(
            delay, vel=MEL_VEL,
            show_notes=SHOW_NOTES,
        ):
            yield e

@typerule(at_least=int, _ret_type=int)
def pause_amt(at_least=1):
    global PAUSE_DISABLED
    if PAUSE_DISABLED:
        return 0
    else:
        low, high = at_least, at_least+3
        return random.randint(low, high)

def with_pause_after(mel, pause=None):
    if pause is None:
        pause = pause_amt()
    if is_string(mel):
        return mel + '-' * pause
    else:
        return None

#@typerule(strn=str|None, _ret_type=str)
def str2mus_strn(strn):
    if is_string(strn):
        # get rid of weird characters
        return strn.replace('!','') \
                   .replace('?','')
    else:
        return strn

@typerule(fname=str, _ret_type=str)
def fname2mus_strn(fname):
    strn = fname.replace('_','-')
    return str2mus_strn(strn)

@typerule(fname=str)
def print_fname(fname):
    log(fname + '()')

def print_response(response):
    if is_string(response):
        log(' '*RESPONSE_OFFSET + str(response))
    else:
        pass


def get_fname(fn):
    if is_function(fn):
        return fn.__name__
    else:
        return fn


def play_func(fn, do_response=None):
    return midi.playe(
        ev_func(fn, do_response)
    )


def ev_func_init(fn):
    global chord, DURATION

    # do start tempo change
    start_dur = get_start_dur(fn)
    if start_dur is not None:
        #log('set DURATION',duration)
        DURATION = start_dur

    # do chord change if any
    start_chord = get_start_chord(fn)
    if start_chord:
        #log('set chord',chord)
        chord = start_chord
        for e in ev_chord_change(): yield e

    # do instrument change if any
    start_inst = get_start_instruments(fn)
    if start_inst is not None:
        #log('set INSTRUMENTS',start_inst)
        choose_instruments(start_inst)


# play function name
def ev_func_name(fname, pause):
    print_fname(fname)
    fname = fname2mus_strn(fname)
    fname_events = midi.ev_strn(
        with_pause_after(fname, pause),
        dur = DURATION, vel = MEL_VEL,
        show_notes = SHOW_NOTES,
    )
    for e in fname_events: yield e


# event-stream-based version of play_func
def ev_func(fn, do_response=None):

    global chord, DURATION #todo not needed anymore, ev_init has it?

    fname = get_fname(fn)

    if not is_lambda(fname):
        for e in ev_func_init(fn):
            yield e

        #todo find a simpler way for last_pitch -
            # maybe allow the ev_pitches to write into
            # some shared value, like a list or dict?
            # (maybe not tho, this seems maybe ok)
        last_pitch = None
        pause1 = pause_amt()
        for e in ev_func_name(fname, pause1):
            last_pitch = midi.maybe_set_pitch(last_pitch, e)
            yield e

        # maybe run function and play response
        if do_response is None:
            do_response = True #coinflip()
        if do_response:
            #todo figure out last_pitch / prev_pitch stuff
            for e in ev_fn_response(fn, pause1=pause1, prev_pitch=last_pitch):
                yield e

def ev_fn_response(fn, pause1=None, prev_pitch=None):
    if is_function(fn):
        response = fn()
        if isinstance(response, types.GeneratorType):
            for section in response:
                #new_prev_pitch = ev_fn_response_1(section, pause1, prev_pitch)
                #prev_pitch = new_prev_pitch
                new_prev_pitch = None
                for e in ev_fn_response_1(
                    section, pause1, prev_pitch=prev_pitch
                ):
                    new_prev_pitch = midi.maybe_set_pitch(new_prev_pitch,e)
                    yield e
                prev_pitch = new_prev_pitch
        else:
            for e in ev_fn_response_1(
                response, pause1,
                prev_pitch = prev_pitch
            ):
                yield e

def ev_fn_response_1(response, pause1=None, prev_pitch=None):
    for e in ev_chord_change(): yield e
    print_response(response)
    response = str2mus_strn(response)

    pause2 = pause_amt(at_least = pause1)
    response = with_pause_after(response, pause2)

    if is_string(response):
        for e in midi.ev_strn(
            response,
            dur = DURATION, 
            prev_pitch = prev_pitch,
            vel = MEL_VEL,
            show_notes = SHOW_NOTES,
        ):
            yield e
    else:
        pass # don't yield anything



def process_chord_change():
    return midi.playe(
        ev_chord_change()
    )

def ev_chord_change():
    global chord, sounding_chord
    if chord is not None:
        if sounding_chord:
            for e in midi.ev_chordname_off(
                sounding_chord, chan=1, show_notes=SHOW_NOTES
            ):
                yield e
        for e in midi.ev_chordname_on(
            chord, vel=CHORD_VEL, chan=1, show_notes=SHOW_NOTES
        ):
            yield e
        print_chord(chord)
        sounding_chord = chord
        chord = None

def chord_offset():
    return RESPONSE_OFFSET / 2

def print_chord(chord):
    log(' '*chord_offset() + "[" + chord + "]")

def musicall(fn): #todo args
    play_func(fn, do_response=True)

def coinflip(unlikeliness=2):
    return random.randint(1,unlikeliness) == 1

def some_parts(*parts):
    i = random.randint(1,len(parts))
    my_parts = parts[:i]
    if under_assumption('working with strings'):
        return ''.join(my_parts)
    else:
        return my_parts

def some_end_parts(*parts):
    i = random.randint(0,len(parts)-1)
    my_parts = parts[i:]
    if under_assumption('working with strings'):
        return ''.join(my_parts)
    else:
        return my_parts

def goof_around(env):
    try:
        while True:
            play_funcs(env)
    except KeyboardInterrupt:
        print("Bye!")
        midi.panic()

def take_from_env(names, env):
    return {name: env[name] for name in names}


def setup():
    # need to give some arg or it won't change instruments, "rnd" to randomly choose
    if len(sys.argv) > 1:
        print("Choosing Instruments from args")
        choose_instruments(sys.argv[1:])
    elif INSTRUMENTS:
        print("Choosing Instruments from INSTRUMENTS setting")
        choose_instruments(INSTRUMENTS)
    else:
        print("Leaving instruments the same")


def choose_instruments(args): #todo clean up / simplify

    if args == 'rnd': args = ['rnd']

    sug0,sug1 = midi.cool_inst_combo()
    do_sug = True # coinflip()

    user_specified_instruments = len(args) > 0 and args[0] != 'rnd'

    # set inst 0
    if user_specified_instruments:
        inst0 = int(args[0])
    elif do_sug:
        inst0 = sug0
    else: 
        inst0 = midi.rand_inst(chan=0)

    # set inst 1
    if len(args) > 1:
        inst1 = int(args[1])
    elif do_sug:
        inst1 = sug1
    else:
        inst1 = midi.rand_inst(chan=1)

    # description
    if user_specified_instruments:
        log("setting custom instruments", (inst0, inst1))
    elif do_sug:
        log("known cool instrument combo", (inst0, inst1))
    else:
        log("experimental random instrument", (inst0, inst1))

    # actually changes patches
    midi.midi_program_change(inst0, chan=0)
    midi.midi_program_change(inst1, chan=1)

    # update INSTRUMENTS var
    INSTRUMENTS = (inst0,inst1)


def change_duration(dur):
    global DURATION
    log("Changing tempo to " + str(dur))
    DURATION = dur

def mult_duration(durmult):
    global DURATION
    log("Multiplying tempo by factor of " + str(durmult))
    DURATION *= durmult

def play_id(strn):
    midi.play_strn(fname2mus_strn(strn), show_notes=SHOW_NOTES, vel=MEL_VEL)


# @start_chord decorator
def start_chord(the_chord):
    def outer(func):
        #log('@start_chord',the_chord)
        func.chord = the_chord
        return func
    return outer

# @start_dur decorator
def start_dur(dur):
    def outer(func):
        #log('@start_dur',dur)
        func.duration = dur
        return func
    return outer

# @start_instrument decorator
def start_instruments(inst):
    def outer(func):
        #log('@start_instrument',inst)
        func.instruments = inst
        return func
    return outer

def get_start_chord(fn):
    if hasattr(fn, 'chord'):
        if is_function(fn.chord):
            return fn.chord()
        else:
            return fn.chord

def get_start_dur(fn):
    if hasattr(fn, 'duration'):
        return fn.duration

def get_start_instruments(fn):
    if hasattr(fn, 'instruments'):
        return fn.instruments

