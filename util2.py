import copy

def is_listy(x):
    return isinstance(x,list) \
        or isinstance(x,tuple) #choose #fixme be more general

def car(L):
    return L[0]

def cdr(L):
    return L[1:]

def env_copy():
    return copy.copy(globals()) \
               .update(locals())

def lispy_funcall(l, env=None):
    # event e is a lispy tuple (fn arg1 arg2 ...)
    if env is None:
        env = env_copy()
        # Q. will this make globals/locals that are edited not actually get edited?
    func_name = car(l)
    args = cdr(l)
    fn = env[func_name]
    return fn(*args)

