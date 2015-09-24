from midi import *
import types, random

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
    for func_name,func in get_funcs(env).items():
        play_func(func)

def with_pause_after(mel):
    return mel + '-'

def call_and_response(mel1,mel2):
    return mel1 + '-' + mel2 + '-'

def fname2mus_strn(fname):
    return fname.replace('_','-')

def print_fname(fname):
    print fname + '()'

def print_response(response):
    print ' '*60 + response

def play_func(fn):

    if is_function(fn):
        fname = fn.__name__
    else:
        fname = fn

    if not is_lambda(fname):

        print_fname(fname)
        fname = fname2mus_strn(fname)
        play_strn(
            with_pause_after(fname)
        )

        do_response = coinflip()
        if do_response:
            response = fn()
            response = fname2mus_strn(response)
            print_response(response)
            play_strn(
                with_pause_after(response)
            )

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

