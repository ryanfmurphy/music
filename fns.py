from music import *
from isness import *
import types, random, code, ast, _ast, readline, os, atexit
import music

CHORD_VEL = 65
RESPONSE_OFFSET = 30
DURATION = .2 #music.swung_dur(.4,.2).next

cur_chord = None
prev_chord = None

pause_disabled = True


def under_assumption(assumption):
    if assumption == 'working with strings':
        return True
    else:
        return False

def options(*things):
    return random.choice(things)

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
    print '...'
    if coinflip(4):
        delay = '-' * options(8,16,24,32) #,48,64)
        play_strn(delay, show_notes=False)

def pause_amt(at_least=1):
    global pause_disabled
    if pause_disabled:
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

def str2mus_strn(strn):
    if is_string(strn):
        # get rid of weird characters
        return strn.replace('!','') \
                   .replace('?','')
    else:
        return strn

def fname2mus_strn(fname):
    strn = fname.replace('_','-')
    return str2mus_strn(strn)

def print_fname(fname):
    print fname + '()'

def print_response(response):
    if is_string(response):
        print ' '*RESPONSE_OFFSET + str(response)


def get_fname(fn):
    if is_function(fn):
        return fn.__name__
    else:
        return fn


def play_func(fn, do_response=None):

    global cur_chord

    fname = get_fname(fn)

    if not is_lambda(fname):

        # do chord change if any
        start_chord = get_start_chord(fn)
        if start_chord:
            cur_chord = start_chord
            process_chord_change()

        # play function name
        print_fname(fname)
        fname = fname2mus_strn(fname)
        pause1 = pause_amt()
        play_strn(
            with_pause_after(fname, pause1),
            show_notes = False,
            dur = DURATION,
        )

        # maybe run function and play response
        if do_response is None:
            do_response = True #coinflip()
        if do_response:
            play_fn_response(fn, pause1=pause1)

def play_fn_response(fn, pause1=None):
    if is_function(fn):
        response = fn()
        if isinstance(response, types.GeneratorType):
            for section in response:
                play_fn_response_1(section, pause1=pause1)
        else:
            play_fn_response_1(response, pause1=pause1)

def play_fn_response_1(response, pause1=None):
    process_chord_change()
    print_response(response)
    response = str2mus_strn(response)

    pause2 = pause_amt(at_least = pause1)
    response = with_pause_after(response, pause2)

    play_strn(
        response,
        show_notes = False,
        dur = DURATION, 
    )

def process_chord_change():
    global cur_chord, prev_chord
    if cur_chord != prev_chord:
        music.chordname_off(prev_chord, chan=1)
        music.chordname_on(cur_chord, vel=CHORD_VEL, chan=1)
        print_chord(cur_chord)
        prev_chord = cur_chord

def get_start_chord(fn):
    if hasattr(fn, 'start_chord'):
        return fn.start_chord

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
            #music.play_strn(cefg())
            play_funcs(env)
    except KeyboardInterrupt:
        print "Bye!"
        music.panic()

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
                play_whatever_node = ast_call_node('music.play_whatever', '_', show_notes=False)
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
        music.panic()
        print "See ya!"

def setup():
    choose_instruments()


def choose_instruments():

    sug0,sug1 = music.cool_inst_combo()
    do_sug = coinflip()

    # set inst 0
    print "Channel 0:",
    if len(sys.argv) > 1:
        inst0 = int(sys.argv[1])
        print "setting custom instrument", inst0
    elif do_sug:
        inst0 = sug0
        print "known cool instrument combo", inst0
    else: 
        inst0 = music.rand_inst(chan=0)
        print "experimental random instrument", inst0
    # actually changes patch
    music.midi_program_change(inst0, chan=0)

    # set inst 1
    print "Channel 1:",
    if len(sys.argv) > 2:
        inst1 = int(sys.argv[2])
        print "setting custom instrument", inst1
    elif do_sug:
        inst1 = sug1
        print "known cool instrument combo", inst1
    else:
        inst1 = music.rand_inst(chan=1)
        print "experimental random instrument", inst1
    # actually changes patch
    music.midi_program_change(inst1, chan=1)

def change_duration(dur):
    global DURATION
    DURATION = dur

def mult_duration(dur):
    global DURATION
    DURATION *= dur

