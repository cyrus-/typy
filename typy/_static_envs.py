"""typy static environments"""

import ast
import types
import builtins

__all__ = ("StaticEnv",)

_builtins_dict = builtins.__dict__
class StaticEnv(object):
    def __init__(self, closure, globals):
        self.closure = closure
        self.globals = globals

    def __getitem__(self, item):
        try:
            return self.closure[item]
        except KeyError:
            try:
                return self.globals[item]
            except KeyError:
                return _builtins_dict[item]

    def __contains__(self, item):
        return item in self.closure or item in self.globals

    @classmethod
    def from_func(cls, f):
        closure = cls._func_closure(f)
        try:
            globals = f.func_globals
        except AttributeError:
            globals = f.__globals__
        return cls(closure, globals)

    @classmethod
    def _func_closure(cls, f):
        try:
            closure = f.func_closure
        except AttributeError:
            closure = f.__closure__
        if closure is None:
            return {}
        else:
            try:
                code = f.func_code
            except AttributeError:
                code = f.__code__
            return dict(cls._get_cell_contents(code.co_freevars, closure))

    @classmethod
    def _get_cell_contents(cls, co_freevars, closure):
        for x, c in zip(co_freevars, closure):
            try:
                yield x, c.cell_contents
            except ValueError:
                continue

    def eval_expr_ast(self, expr):
        expr = ast.Expression(expr)
        code = compile(expr, "<eval_expr_ast>", "eval")
        return eval(code, self.globals, self.closure)

    def eval_module_ast(self, module_ast):
        print(ast.dump(module_ast, include_attributes=True))
        code = compile(module_ast, "<eval_module_ast>", "exec")
        _module = types.ModuleType("TestModule", "Module test") # TODO properly name them
        _module_dict = _module.__dict__
        _module_dict.update(self.globals)
        _module_dict.update(self.closure)
        exec(code, _module_dict)
        return _module

