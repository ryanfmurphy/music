import types

def is_function(x):
    return isinstance(x, types.FunctionType)

def is_lambda(fn):
    if is_function(fn): fn = fn.__name__
    return fn == '<lambda>'

def is_module(x):
    return isinstance(x, types.ModuleType)

def is_object(x):
    return isinstance(x, object)

def is_string(x):
    return isinstance(x, str)

