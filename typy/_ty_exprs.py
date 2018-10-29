"""typy type expression system"""

import ast

from ._errors import TypeFormationError

class UTyExpr(object):
    @classmethod
    def parse(cls, expr):
        if isinstance(expr, ast.Name):
            return UName(expr)
        elif isinstance(expr, ast.Subscript):
            return UCanonicalTy(expr.value, expr.slice)
        elif isinstance(expr, ast.Attribute):
            return UProjection(expr.value, expr.attr)
        else:
            raise TypeFormationError("Malformed type.", expr)

class UCanonicalTy(UTyExpr):
    def __init__(self, fragment_ast, idx_ast):
        self.fragment_ast = fragment_ast
        self.idx_ast = idx_ast

class UName(UTyExpr):
    def __init__(self, name_ast):
        self.name_ast = name_ast
        self.id = name_ast.id

class UProjection(UTyExpr):
    def __init__(self, path_ast, lbl):
        self.path_ast = path_ast
        self.lbl = lbl

class TyExpr(object):
    pass

class CanonicalTy(TyExpr):
    def __init__(self, fragment, idx):
        self.fragment = fragment
        self.idx = idx

    @classmethod
    def new(cls, ctx, fragment, idx_ast):
        return cls(fragment, fragment.init_idx(ctx, idx_ast))

    def __str__(self):
        return self.fragment.__name__ + "[" + str(self.idx) + "]"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, CanonicalTy):
            return (self.fragment == other.fragment) \
                   and (self.idx == other.idx)
        else:
            return False # need contextual equivalence here

    def __ne__(self, other):
        return not self.__eq__(other)

class TyExprVar(TyExpr):
    def __init__(self, ctx, name_ast, uniq_id):
        self.ctx = ctx
        self.name_ast = name_ast
        self.uniq_id = uniq_id

    def __eq__(self, other):
        if isinstance(other, TyExprVar):
            return self.ctx == other.ctx and self.uniq_id == other.uniq_id
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

class TyExprPrj(TyExpr):
    def __init__(self, path_ast, path_val, lbl):
        self.path_ast = path_ast
        self.path_val = path_val
        self.lbl = lbl

class Kind(object):
    @classmethod
    def parse(cls, expr):
        if isinstance(expr, ast.Name) and expr.id == "type":
            return TypeKind
        else:
            return None

class TypeKind(Kind):
    def __init__(self):
        Kind.__init__(self)

    def __repr__(self):
        return "type"

    def __str__(self):
        return "type"
TypeKind = TypeKind()

class SingletonKind(Kind):
    def __init__(self, ty):
        self.ty = ty


