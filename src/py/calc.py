# lisp calculator interpreter (Python 2)

# calcpy uses Python's built in math functions
import math
import operator as op

# sample program
# program = "(begin (define r 10) (* pi (* r r)))"

# interpreters
# 1. parse(program)
# 2. eval the AST of the parse program
# eval(parse(program))

# calcpy includes constants (numbers), variables, conditionals, variable definitions,
# and procedure calls (using the Python math lib)

# An environment is a mapping of {variable: value}
Env = dict

# Scheme objects
Symbol = str          # A Scheme Symbol is implemented as a Python str
List   = list         # A Scheme List is implemented as a Python list
Number = (int, float) # A Scheme Number is implemented as a Python int or float


def tokenize(chars):
    "Convert a string of chars into a list of tokens."
    # this adds spaces around parens to split around whitespace
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()

def atom(token):
    "Numbers become numbers; every other token is a symbol."
    try: return int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return Symbol(token)

# creates list-based AST
def read_from_tokens(tokens):
    "Read an expression from a sequence of tokens."
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF while reading')
    token = tokens.pop(0)
    if '(' == token:
        L = []
        while tokens[0] != ')':
            L.append(read_from_tokens(tokens))
        tokens.pop(0) # pop off ')'
        return L
    elif ')' == token:
        raise SyntaxError('unexpected )')
    else:
        return atom(token)

def parse(program):
    "Read a Scheme expression from a string"
    return read_from_tokens(tokenize(program))

def standard_env():
    env = Env()
    env.update(vars(math)) # add math lib functions (sin, cos,...)
    env.update({
        '+':op.add, '-':op.sub, '*':op.mul, '/':op.div,
        '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq,
        'abs':     abs,
        'append':  op.add,
        'apply':   apply,
        # in Scheme, begin is a special form that takes a sequence of arguments,
        # evaluates each one, and returns the last one (discrading values and
        # only using side effects). we implement begin as a function for ease
        'begin':   lambda *x: x[-1],
        'car':     lambda x: x[0],
        'cdr':     lambda x: x[1:],
        'cons':    lambda x,y: [x] + y,
        'eq?':     op.is_,
        'equal?':  op.eq,
        'length':  len,
        'list':    lambda *x: list(x),
        'list?':   lambda x: isinstance(x,list),
        'map':     map,
        'max':     max,
        'min':     min,
        'not':     op.not_,
        'null?':   lambda x: x == [],
        'number?': lambda x: isinstance(x, Number),
        'procedure?': callable,
        'round':   round,
        'symbol?': lambda x: isinstance(x, Symbol),
    })

    return env

global_env = standard_env()

def eval(x, env=global_env):
    "Evaluate an expression in an environment"
    if isinstance(x, Symbol):   # variable reference
        return env[x]
    elif not isinstance(x, List): # constant literal
        return x
    elif x[0] == 'if':  # conditional
        # single underscore holds result of last executed statement and is used
        # as a throwaway. in this case, it is a throwaway
        (_, test, conseq, alt) = x
        exp = (conseq if eval(test, env) else alt)
        return eval(exp, env)
    elif x[0] == 'define':  # definition
        (_, var, exp) = x
        env[var] = eval(exp, env)
    else:
        proc = eval(x[0], env)
        args = [eval(arg, env) for arg in x[1:]]
        return proc(*args)

# eval(parse("(if (> (+ 10 5) 0) (+ 5 6) (+ 7 8))"))
# eval(parse("(define r 10)"))
# eval(parse("(* pi (* r r))"))
