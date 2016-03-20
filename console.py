#todo figure out if we don't need all these imports
from __future__ import print_function
import midi, music #todo what's calling music?
from isness import *
import types, random, code, ast, _ast, readline, sys, os, atexit
from strict_typing import types as typerule

from fns import play_func

SHOW_NOTES = True

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
                play_whatever_node = ast_call_node('music.play_whatever', '_', show_notes=SHOW_NOTES)
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
        print("See ya!")


if __name__ == '__main__':
    console(globals())


