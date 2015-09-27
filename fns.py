from midi import *
import types, random, code, ast, _ast
import midi

CHORD_VEL = 65

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

def is_function(x):
    return isinstance(x, types.FunctionType)

def is_lambda(fn):
    if is_function(fn): fn = fn.__name__
    return fn == '<lambda>'

def is_module(x):
    return isinstance(x, types.ModuleType)

def is_object(x):
    return isinstance(x, object)

def get_funcs(env):
    return {k:v for k,v in env.items()
            if is_function(v)}

def play_funcs(env):
    if is_module(env):
        env = env.__dict__
    funcs = get_funcs(env).items()
    random.shuffle(funcs)
    for func_name,func in funcs:
        play_func(func)

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
    return mel + '-' * pause

def fname2mus_strn(fname):
    return fname.replace('_','-')

def print_fname(fname):
    print fname + '()'

def print_response(response):
    print ' '*60 + response


def get_fname(fn):
    if is_function(fn):
        return fn.__name__
    else:
        return fn


def play_func(fn, do_response=None):

    fname = get_fname(fn)

    if not is_lambda(fname):

        print_fname(fname)
        fname = fname2mus_strn(fname)
        pause1 = pause_amt()
        play_strn(
            with_pause_after(fname, pause1),
            show_notes = False,
        )

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
    pause2 = pause_amt(at_least = pause1)
    play_strn(
        with_pause_after(response, pause2),
        show_notes = False,
    )

def process_chord_change():
    global cur_chord, prev_chord
    if cur_chord != prev_chord:
        midi.chordname_off(prev_chord, chan=1)
        midi.chordname_on(cur_chord, vel=CHORD_VEL, chan=1)
        print "chord:", cur_chord
        prev_chord = cur_chord

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
            #midi.play_strn(cefg())
            play_funcs(env)
    except KeyboardInterrupt:
        print "Bye!"
        midi.panic()

def take_from_env(names, env):
    return {name: env[name] for name in names}

class MusicConsole(code.InteractiveConsole):

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
                play_whatever_node = ast_call_node('midi.play_whatever', '_', show_notes=False)
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
        MusicConsole(env).interact()
    except KeyboardInterrupt:
        midi.panic()
        print "See ya!"

def setup():
    if len(sys.argv) > 1:
        inst0 = int(sys.argv[1])
        midi_program_change(inst0, chan=0)
    else:
        inst0 = midi.rand_inst(chan=0)
    print "chan 0 gets instrument " + str(inst0)
    if len(sys.argv) > 2:
        inst1 = int(sys.argv[2])
        midi_program_change(inst1, chan=1)
    else:
        inst1 = midi.rand_inst(chan=1)
    print "chan 1 gets instrument " + str(inst1)

