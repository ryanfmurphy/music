import copy

def is_listy(x):
    return isinstance(x,list) \
        or isinstance(x,tuple) #choose #fixme be more general

def lispy_funcall(l, env=None):
    # event e is a lispy tuple (fn arg1 arg2 ...)
    if env is None:
        env = copy.copy(globals()).update(locals())
    func_name = l[0]
    args = l[1:]
    fn = env[func_name]
    return fn(*args)

