from typy import (Type, Kind, KindFormationError, TyExpr, TypeFormationError, 
                  _in_eq_assumptions, eq_assumptions)
import typy.util as _util

class _canary(Type):
    @classmethod
    def init_idx(cls, idx):
        return None
_canary = _canary[()]

class KArrow(Kind):
    """The kind of type functions."""
    def __init__(self, arg_kinds, result_kind):
        if not isinstance(arg_kinds, tuple):
            raise KindFormationError("Malformed kind.")
        for arg_kind in arg_kinds:
            if not isinstance(arg_kind, Kind):
                raise KindFormationError("Malformed kind.")
        if not isinstance(result_kind, Kind):
            raise KindFormationError("Malformed kind.")
        self.arg_kinds = arg_kinds
        self.result_kind = result_kind

    def __str__(self):
        return ("(" 
                + ", ".join(str(k) for k in self.arg_kinds)
                + ") > " 
                + str(self.result_kind))

    def __eq__(self, other):
        if self is other: return True
        else:
            if isinstance(other, KArrow):
                return (self.arg_kinds == other.arg_kinds
                        and self.result_kind == other.result_kind)
            else:
                return False

class TyVar(TyExpr):
    def __init__(self, ctx, id):
        self.ctx = ctx
        self.id = id
        # TODO: check that id is in ctx

    def __str__(self):
        return self.id

    def __eq__(self, other):
        return (self is other 
                or (isinstance(other, TyVar)
                    and other.ctx is self.ctx
                    and other.id == self.id))

    def normalize(self):
        return self

class TyRecFn(TyExpr):
    def __init__(self, f):
        if not _util.is_py_fn(f):
            raise TypeFormationError(
                "f is not a valid Python function.")
        n_args_f = _util.fn_argcount(f)
        if n_args_f != 1:
            raise TypeFormationError(
                "Must take self as an argument.")
        self_ap = self.self_ap = f(self)
        if not _util.is_py_fn(self_ap):
            raise TypeFormationError(
                "f(self) is not a valid Python function.")
        n_args_self_ap = _util.fn_argcount(self_ap)
        if n_args_self_ap != 1:
            # TODO support multi-argument type functions (?)
            raise TypeFormationError(
                "f(self) should take exactly 1 argument.")
        self.f = f

    def __eq__(self, other):
        if self is other: return True
        else:
            return self(_canary) == other(_canary)

    def __call__(self, *args):
        return TyApExpr(self, args)

    def normalize(self):
        return self

    def __str__(self):
        return "recfn(" + str(self.f) + ")"

# printed = 0
class TyApExpr(TyExpr):
    def __init__(self, f, args):
        self.f = f
        if len(args) != 1:
            raise TypeFormationError(
                "len(args) != 1")
        self.args = args

    def __eq__(self, other):
        if self is other: return True
        else:
            if isinstance(other, TyApExpr):
                if other.f is self.f and other.args[0] == self.args[0]:
                    return True
            # global printed
            # if printed < 100000000:
            #     print ("CHECKIN " 
            #        + str(self) + " == " + str(other) 
            #        + " with " + str(eq_assumptions))
            #     printed += 1
            # else:
            #     printed = 0
            #     raise Exception("...")
            if _in_eq_assumptions(self, other):
                return True
            o_norm = other.normalize()
            if _in_eq_assumptions(self, o_norm):
                return True
            s_norm = self.normalize()
            eq_assumptions.append((self, o_norm))
            eq_assumptions.append((self, other))
            b = (s_norm == o_norm)
            eq_assumptions.pop()
            eq_assumptions.pop()
            return b
    
    def normalize(self):
        f, a = self.f, self.args[0]
        f_norm = f.normalize()
        a_norm = a.normalize()
        return (f.f(f_norm)(a_norm)).normalize()

    def __str__(self):
        return str(self.f) + "(" + str(self.args[0]) + ")"


