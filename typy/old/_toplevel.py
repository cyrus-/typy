"""logic for interacting with Python at the top level."""
import ast 
import inspect  # for accessing source code for functions
import textwrap  # for stripping leading spaces from source code

import _typelevel
import _inctypes
import _context
import _errors

class TopLevelType(_typelevel.Type):
    """Top-level types have some additional responsibilities."""
    def __new__(cls, idx_or_f, shortname=None, equirec_idx_schema=None,
                from_construct_ty=False):
        # override __new__ to allow the class to be used as fn decorator
        # at the top level
        if not from_construct_ty and inspect.isfunction(idx_or_f):
            (tree, static_env) = cls._reflect_func(idx_or_f)
            return TopLevelValue(tree, static_env, cls[...])
        else: 
            return super(TopLevelType, cls).__new__(
                cls, idx_or_f, shortname, 
                equirec_idx_schema,
                from_construct_ty)

    def __call__(self, f):
        (tree, static_env) = self._reflect_func(f)
        return TopLevelValue(tree, static_env, self)

    @staticmethod
    def _reflect_func(f): 
        source = textwrap.dedent(inspect.getsource(f))
        tree = ast.parse(source).body[0] 
        return (tree, StaticEnv.from_func(f))

class StaticEnv(object):
    def __init__(self, closure, globals):
        self.closure = closure
        self.globals = globals

    def __getitem__(self, item):
        try: 
            return self.closure[item]
        except KeyError:
            return self.globals[item]

    @classmethod
    def from_func(cls, f):
        closure = cls._func_closure(f)
        globals = f.func_globals
        return cls(closure, globals)

    def eval_expr_ast(self, tree):
        tree = ast.Expression(tree)
        code = compile(tree, "<eval_expr_ast>", "eval")
        return eval(code, self.globals, self.closure)

    @classmethod
    def _func_closure(cls, f):
        closure = f.func_closure
        if closure is None: 
            return {}
        else:
            return dict(cls._get_cell_contents(f.func_code.co_freevars, closure))

    @classmethod
    def _get_cell_contents(cls, co_freevars, closure):
        for x, c in zip(co_freevars, closure):
            try:
                yield x, c.cell_contents
            except ValueError:
                continue

class TopLevelValue(object):
    """All top-level typy values are instances of TopLevelValue."""
    def __init__(self, tree, static_env, ascription):
        # TODO: turn into proper errors
        if not isinstance(tree, ast.FunctionDef):
            raise _errors.ExtensionError()
        if not isinstance(static_env, StaticEnv):
            raise _errors.ExtensionError()
        if not isinstance(ascription, (_typelevel.Type, _inctypes.IncompleteType)): 
            raise _errors.ExtensionError()
        tc = _typelevel.tycon(ascription)
        if not issubclass(tc, TopLevelType):
            raise _errors.ExtensionError()
        self.tree = tree
        self.static_env = static_env
        self.ascription = ascription

        tc.preprocess_FunctionDef_toplevel(self, tree)

    typechecked = False
    compiled = False

    def typecheck(self):
        if self.typechecked: return self.tree.ty
        tree, ascription = self.tree, self.ascription
        ctx = self.ctx = _context.Context(self)
        _typelevel.tycon(ascription).init_ctx(ctx)
        if isinstance(ascription, _typelevel.Type):
            ctx.ana(tree, ascription)
        else: # IncompleteType
            ctx.ana_intro_inc(tree, ascription)
        ty = tree.ty
        self.typechecked = True
        return ty

    def compile(self):
        self.typecheck()
        if self.compiled: 
            return
        tree, ctx = self.tree, self.ctx
        ty = tree.ty
        translation = ty.translate_FunctionDef(ctx, tree)
        self.translation = translation
        self.compiled = True
        return translation

    def __call__(self, *args):
        # TODO: implement this
        raise NotImplementedError()


