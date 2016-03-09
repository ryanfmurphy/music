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

chord = None
sounding_chord = None

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
            midi.playe(eventsg_func(func))
            #play_func(func)
        midi.playe(eventsg_maybe_delay())

def maybe_delay():
    if SOMETIMES_DELAY and coinflip(2):
        delay_len = options(8,16,24,32) #,48,64)
        print '.' * delay_len
        delay = '-' * delay_len
        midi.play_strn(delay, show_notes=SHOW_NOTES, vel=MEL_VEL)

def eventsg_maybe_delay():
    if SOMETIMES_DELAY and coinflip(2):
        delay_len = options(8,16,24,32) #,48,64)
        print '.' * delay_len
        delay = '-' * delay_len
        for e in midi.eventsg_strn(delay, show_notes=SHOW_NOTES, vel=MEL_VEL):
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
    print fname + '()'

def print_response(response):
    if is_string(response):
        print ' '*RESPONSE_OFFSET + str(response)
    else:
        pass


def get_fname(fn):
    if is_function(fn):
        return fn.__name__
    else:
        return fn


def play_func(fn, do_response=None):

    global chord, DURATION

    fname = get_fname(fn)

    if not is_lambda(fname):

        # do start tempo change
        start_dur = get_start_dur(fn)
        if start_dur is not None:
            DURATION = start_dur

        # do chord change if any
        start_chord = get_start_chord(fn)
        if start_chord:
            chord = start_chord
            process_chord_change()

        # play function name
        print_fname(fname)
        fname = fname2mus_strn(fname)
        pause1 = pause_amt()
        last_pitch = midi.play_strn(
            with_pause_after(fname, pause1),
            show_notes = SHOW_NOTES,
            dur = DURATION,
            vel = MEL_VEL,
        )

        # maybe run function and play response
        if do_response is None:
            do_response = True #coinflip()
        if do_response:
            play_fn_response(fn, pause1=pause1, prev_pitch=last_pitch)

def play_fn_response(fn, pause1=None, prev_pitch=None):
    if is_function(fn):
        response = fn()
        if isinstance(response, types.GeneratorType):
            for section in response:
                new_prev_pitch = play_fn_response_1(section, pause1, prev_pitch)
                prev_pitch = new_prev_pitch
        else:
            play_fn_response_1(response, pause1, prev_pitch)

def play_fn_response_1(response, pause1=None, prev_pitch=None):
    process_chord_change()
    print_response(response)
    response = str2mus_strn(response)

    pause2 = pause_amt(at_least = pause1)
    response = with_pause_after(response, pause2)

    return midi.play_strn(
        response,
        show_notes = SHOW_NOTES,
        dur = DURATION, 
        prev_pitch = prev_pitch,
        vel = MEL_VEL,
    )



# event-stream-based version of play_func
def eventsg_func(fn, do_response=None):

    global chord, DURATION

    fname = get_fname(fn)

    if not is_lambda(fname):

        # do start tempo change
        start_dur = get_start_dur(fn)
        if start_dur is not None:
            DURATION = start_dur

        # do chord change if any
        start_chord = get_start_chord(fn)
        if start_chord:
            chord = start_chord
            for e in eventsg_chord_change(): yield e

        # play function name
        print_fname(fname)
        fname = fname2mus_strn(fname)
        pause1 = pause_amt()
        fname_events = midi.eventsg_strn(
            with_pause_after(fname, pause1),
            show_notes = SHOW_NOTES,
            dur = DURATION,
            vel = MEL_VEL,
        )
        for e in fname_events: yield e

        # maybe run function and play response
        if do_response is None:
            do_response = True #coinflip()
        if do_response:
            eventsg_fn_response(fn, pause1=pause1) #todo fix prev_pitch, prev_pitch=last_pitch)

def eventsg_fn_response(fn, pause1=None, prev_pitch=None):
    if is_function(fn):
        response = fn()
        if isinstance(response, types.GeneratorType):
            for section in response:
                #new_prev_pitch = eventsg_fn_response_1(section, pause1, prev_pitch)
                #prev_pitch = new_prev_pitch
                for e in eventsg_fn_response_1(section, pause1, prev_pitch): yield e
        else:
            for e in eventsg_fn_response_1(response, pause1): yield e #todo fix: , prev_pitch)

def eventsg_fn_response_1(response, pause1=None, prev_pitch=None):
    for e in eventsg_chord_change(): yield e
    print_response(response)
    response = str2mus_strn(response)

    pause2 = pause_amt(at_least = pause1)
    response = with_pause_after(response, pause2)

    for e in midi.eventsg_strn(
        response,
        show_notes = SHOW_NOTES,
        dur = DURATION, 
        prev_pitch = prev_pitch,
        vel = MEL_VEL,
    ):
        yield e



def process_chord_change():
    global chord, sounding_chord
    if chord is not None:
        if sounding_chord:
            midi.chordname_off(sounding_chord, chan=1, show_notes=SHOW_NOTES)
        midi.chordname_on(chord, vel=CHORD_VEL, chan=1, show_notes=SHOW_NOTES)
        print_chord(chord)
        sounding_chord = chord
        chord = None

def eventsg_chord_change():
    return [] #todo
    '''
    global chord, sounding_chord
    if chord is not None:
        if sounding_chord:
            midi.chordname_off(sounding_chord, chan=1, show_notes=SHOW_NOTES)
        midi.chordname_on(chord, vel=CHORD_VEL, chan=1, show_notes=SHOW_NOTES)
        print_chord(chord)
        sounding_chord = chord
        chord = None
    '''

def get_start_chord(fn):
    if hasattr(fn, 'chord'):
        if is_function(fn.chord):
            return fn.chord()
        else:
            return fn.chord

def get_start_dur(fn):
    if hasattr(fn, 'duration'):
        return fn.duration

def chord_offset():
    return RESPONSE_OFFSET / 2

def print_chord(chord):
    print ' '*chord_offset() + "[" + chord + "]"

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
        print "Bye!"
        midi.panic()

def take_from_env(names, env):
    return {name: env[name] for name in names}


class MusicConsole(code.InteractiveConsole):

    # the next 3 functions are about readline history / up-arrow completion

    def __init__(self, locals=None, filename="<console>",
                 histfile=os.path.expanduser("~/.music-console-history")):
        code.InteractiveConsole.__init__(self, locals, filename)
        self.init_history(histfile)

    def init_history(self, histfile):
        readline.parse_and_bind("tab: complete")
        if hasattr(readline, "read_history_file"):
            try:
                readline.read_history_file(histfile)
            except IOError:
                pass
            atexit.register(self.save_history, histfile)

    def save_history(self, histfile):
        readline.write_history_file(histfile)


    def runsource(self, source, filename='<input>', symbol='single'):
        # code taken from InteractiveInterpreter.runsource in code.py
        try:
            code = self.compile(source, filename, symbol)
        except (OverflowError, SyntaxError, ValueError):
            # Case 1
            self.showsyntaxerror(filename)
            return False

        if code is None:
            # Case 2
            return True

        # Case 3
        self.maybe_make_music(source)
        self.runcode(code, source)
        return False

    def runcode(self, the_code, source, filename='<input>'):
        # code taken from InteractiveInterpreter.runsource in code.py
        try:
            tree = ast.parse(source)
            try:
                expr = ast.parse(source, mode='eval')
            except:
                expr = None
            #todo get this to work for multiple expr's, not just 1:
            if expr and len(tree.body) == 1:
                # _ = expr_value
                tree.body[0] = ast_wrap_in_assn('_', tree.body[0])
                # print _
                underscore = _ast.Name(id="_", ctx=_ast.Load())
                print_node = ast_print_node([_ast.Str(s=' '*50), underscore])
                tree.body.append(print_node)
                # play_whatever
                    #todo doesn't work for generators yet
                play_whatever_node = ast_call_node('midi.play_whatever', '_', show_notes=SHOW_NOTES)
                tree.body.append(play_whatever_node)
            #print ast.dump(tree)
            code_obj = compile(tree, '<input>', 'exec')
            exec code_obj in self.locals
        except SystemExit:
            raise
        except:
            self.showtraceback()
        else:
            if code.softspace(sys.stdout, 0):
                print

    def maybe_make_music(self, source):
        tree = ast.parse(source)
        #print ast.dump(tree)
        fn = ast_funcall_to_fname(tree)
        if fn:
            #print "yep! functioncall"
            play_func(fn)


def ast_wrap_in_assn(var_name, ast_expr):
    assn = _ast.Assign(
        targets = [_ast.Name(id=var_name, ctx=_ast.Store())],
        value = ast_expr.value
    )
    ast.fix_missing_locations(assn)
    return assn

def ast_parse1(source):
    return ast.parse(source).body[0]

def ast_expr(tree):
    if isinstance(tree, _ast.Module):
        body = tree.body
        if len(body) == 1:
            item = body[0]
            if isinstance(item, _ast.Expr):
                return item

def ast_funcall_to_fname(tree):
    expr = ast_expr(tree)
    if expr:
        if isinstance(expr.value, _ast.Call):
            call = expr.value
            return call.func.id

def ast_print_node(values):
    print_node = _ast.Print(
        values=values,
        nl=True
    )
    ast.fix_missing_locations(print_node)
    return print_node

def ast_call_node(fname, *args, **kwargs):
    innards = ','.join(str(arg) for arg in args)
    kwinnards = ','.join(str(kw)+'='+str(val) for kw,val in kwargs.items())
    if kwinnards:
        innards += ',' + kwinnards
    source = fname+'('+innards+')'
    #print "source:", source
    call = ast_parse1(source)
    ast.fix_missing_locations(call)
    return call

#todo get console to have up-arrow history (readline)
    # actually it works with python -i
def console(env):
    try:
        console = MusicConsole(env)
        console.interact()
    except KeyboardInterrupt:
        midi.panic()
        print "See ya!"

def setup():
    # need to give some arg or it won't change instruments, "rnd" to randomly choose
    if len(sys.argv) > 1:
        print "Choosing Instruments from args"
        choose_instruments(sys.argv[1:])
    elif INSTRUMENTS:
        print "Choosing Instruments from INSTRUMENTS setting"
        choose_instruments(INSTRUMENTS)
    else:
        print "Leaving instruments the same"

#INST0 = 19
#INST1 = 0

def choose_instruments(args): #todo clean up / simplify
    #global INST0, INST1
    #INST0 += 1
    #midi.midi_program_change(INST0, chan=0)
    #print (INST0, INST1)
    #return

    sug0,sug1 = midi.cool_inst_combo()
    do_sug = coinflip()

    # set inst 0
    if len(args) > 0 and args[0] != 'rnd':
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
    if len(args) > 0:   
        print "setting custom instruments", (inst0, inst1)
    elif do_sug:
        print "known cool instrument combo", (inst0, inst1)
    else:
        print "experimental random instrument", (inst0, inst1)

    # actually changes patches
    midi.midi_program_change(inst0, chan=0)
    midi.midi_program_change(inst1, chan=1)


def change_duration(dur):
    global DURATION
    print "Changing tempo to " + str(dur)
    DURATION = dur

def mult_duration(durmult):
    global DURATION
    print "Multiplying tempo by factor of " + str(durmult)
    DURATION *= durmult

def play_id(strn):
    midi.play_strn(fname2mus_strn(strn), show_notes=SHOW_NOTES, vel=MEL_VEL)

# the start_chord decorator
def start_chord(the_chord):
    def outer(func):
        func.chord = the_chord
        return func
    return outer

# the start_chord decorator
def start_dur(dur):
    def outer(func):
        func.duration = dur
        return func
    return outer

