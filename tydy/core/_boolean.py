"""Python booleans"""
import ast

import typy
import typy.util as _util
import typy.util.astx as astx

class boolean_(typy.Type):
    @classmethod
    def init_idx(cls, idx):
        if idx != ():
            raise typy.TypeFormationError("Index of boolean type must be ().")
        return idx

    @classmethod
    def init_inc_idx(cls, inc_idx):
        if inc_idx != () and inc_idx != Ellipsis:
            raise typy.TypeFormationError(
                "Incomplete index of boolean type must be () or Ellipsis.")
        return inc_idx

    def anon_to_str(self):
        return "boolean"

    def ana_Name_constructor(self, ctx, e):
        id = e.id
        if id != "True" and id != "False":
            raise typy.TypeError(
                "Must introduce a value of boolean type with either True or False.",
                e)

    @classmethod
    def syn_idx_Name_constructor(cls, ctx, e, inc_idx):
        id = e.id
        if id != "True" and id != "False":
            raise typy.TypeError(
                "Must introduce a value of boolean type with either True or False.",
                e)
        return ()

    def translate_Name_constructor(self, ctx, e):
        return astx.copy_node(e)

    def syn_UnaryOp(self, ctx, e):
        if isinstance(e.op, ast.Not):
            return self
        else:
            raise typy.TypeError(
                """Type bool does not support this unary operator.""",
                e)

    def translate_UnaryOp(self, ctx, e):
        translation = astx.copy_node(e)
        translation.operand = ctx.translate(e.operand)
        return translation

    def syn_Compare(self, ctx, e):
        left, ops, comparators = e.left, e.ops, e.comparators
        for op in ops:
            if not isinstance(op, (ast.Eq, ast.NotEq, ast.Is, ast.IsNot)):
                raise typy.TypeError("Type bool does not support this operator.", op)
        for e_ in _util.tpl_cons(left, comparators):
            if hasattr(e_, 'match'): 
                continue # already synthesized
            ctx.ana(e_, self)
        return self

    def translate_Compare(self, ctx, e):
        translation = astx.copy_node(e)
        translation.left = ctx.translate(e.left)
        translation.comparators = (
            ctx.translate(comparator)
            for comparator in e.comparators)
        return translation

    def syn_BoolOp(self, ctx, e):
        values = e.values
        for value in values:
            ctx.ana(value, self)
        return self

    def translate_BoolOp(self, ctx, e):
        translation = astx.copy_node(e)
        translation.values = tuple(
            ctx.translate(value)
            for value in e.values)
        return translation

    def ana_pat_Name_constructor(self, ctx, pat):
        id = pat.id
        if id != "True" and id != "False":
            raise typy.TypeError("Boolean values only match 'True' and 'False'")
        return typy.odict()

    def translate_pat_Name_constructor(self, ctx, pat, scrutinee):
        id = pat.id
        if id == "True":
            return (scrutinee, typy.odict())
        elif id == "False":
            return (ast.UnaryOp(op=ast.Not(), operand=scrutinee), typy.odict())

boolean = boolean_[()]

