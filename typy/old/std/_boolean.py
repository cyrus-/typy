"""typy booleans"""
import ast

import typy
import typy.util.astx as _astx
import typy._errors as _errors

class boolean(typy.Fragment):
    @classmethod
    def init_idx_value(cls, idx_value):
        if idx_value != ():
            raise _errors.TypeFormationError(
                """Index of boolean type must be ().""")
        return idx

    @classmethod
    def anon_to_str(cls, idx_value):
        return "boolean"

    @classmethod
    def ana_Name_constructor(cls, ctx, e, ty):
        id = e.id
        if id == "True" or id == "False": return
        else: raise _errors.TyError(
            "Must introduce a value of boolean type with either True or False.",
            e)

    @classmethod
    def translate_Name_constructor(cls, ctx, e, ty):
        return astx.copy_node(e)

    @classmethod
    def syn_UnaryOp(cls, ctx, e, ty):
        if isinstance(e.op, ast.Not):
            return ty
        else:
            raise _errors.TyError(
                "Type bool does not support this unary operator.",
                e)

    @classmethod
    def translate_UnaryOp(cls, ctx, e, ty):
        translation = astx.copy_node(e)
        translation.operand = ctx.translate(e.operand)
        return translation

    # TODO: compare
    # TODO: boolop
    # TODO: pattern matching
    # TODO: if

