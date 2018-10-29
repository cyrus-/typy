"""Bases deal with things that there isn't anyone else to deal with."""
from _errors import OpTranslationLogicMissing, OpNotSupported

class Base(object):
    """Bases deal with things that there isn't anyone else to deal with."""
    @classmethod
    def init_ctx(cls, ctx): 
        pass

    @classmethod
    def preprocess_FunctionDef_toplevel(cls, fn, tree):
        # TODO is this necessary?
        pass 

    # Name

    @classmethod 
    def syn_Name(cls, ctx, e):
        raise OpNotSupported(cls, "class method", "syn_Name", 
                             "name", e)

    def translate_Name(self, ctx, tree):
        raise OpTranslationLogicMissing(
            self, "method", "translate_Name", 
            "name", tree)

    # match expressions
    # TODO: move this into tydy

    @classmethod
    def ana_match_expr(cls, ctx, e, ty):
        raise OpNotSupported(
            cls, "class method", "ana_match_expr", 
            "match expression (analytic position)", e)

    @classmethod
    def syn_match_expr(cls, ctx, e):
        raise OpNotSupported(cls, "class method", "syn_match_expr", 
                             "match expression (synthetic position)", e)

    @classmethod
    def translate_match_expr(cls, ctx, e):
        raise OpTranslationLogicMissing(
            cls, "method", "translate_match_expr", 
            "match expression", e)

    # if expressions

    @classmethod
    def ana_IfExp(cls, ctx, e, ty):
        raise OpNotSupported(cls, "class method", "ana_IfExp", 
                             "if expression (analytic position)", e)

    @classmethod
    def syn_IfExp(cls, ctx, e):
        raise OpNotSupported(cls, "class method", "syn_IfExp", 
                             "if expression (synthetic position)", e)

    @classmethod
    def translate_IfExp(cls, ctx, e):
        raise OpTranslationLogicMissing(
            cls, "class method", "translate_IfExp", 
            "if expression", e)

