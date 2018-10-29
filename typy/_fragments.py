"""typy fragments"""

import inspect

from ._errors import TyError, FragmentError

__all__ = ('Fragment', 'is_fragment')

class Fragment(object):
    def __init__(self):
        raise NotImplementedError()

    @classmethod
    def init_idx(cls, ctx, idx_ast):
        raise FragmentError(cls.__name__ + " does not implement init_idx.", cls)

    @classmethod
    def idx_eq(cls, ctx, idx1, idx2):
        return idx1 == idx2

    precedence = set()

    ## 
    ## intro expression forms
    ## 

    @classmethod
    def ana_Lambda(cls, ctx, e, idx):
        raise TyError(cls.__name__ + " does not support lambda literals.", e)

    @classmethod
    def trans_Lambda(cls, ctx, e, idx):
        raise FragmentError(
            cls.__name__ + " missing translation method: trans_Lambda.", 
            cls)

    @classmethod
    def ana_Dict(cls, ctx, e, idx):
        raise TyError(
            cls.__name__ + " does not support dictionary literals.", 
            e)

    @classmethod
    def trans_Dict(cls, ctx, e, idx):
        raise FragmentError(cls.__name__ + " missing translation method: trans_Dict.", 
                            cls)

    @classmethod
    def ana_Set(cls, ctx, e, idx):
        raise TyError(cls.__name__ + " does not support set literals.", e)

    @classmethod
    def trans_Set(cls, ctx, e, idx):
        raise FragmentError(cls.__name__ + " missing translation method: trans_Set.", cls)

    @classmethod
    def ana_Num(cls, ctx, e, idx):
        raise TyError(cls.__name__ + " does not support number literals.", e)

    @classmethod
    def trans_Num(cls, ctx, e, idx):
        raise FragmentError(cls.__name__ + " missing translation method: trans_Num.", cls)

    @classmethod
    def ana_Str(cls, ctx, e, idx):
        raise TyError(cls.__name__ + " does not support string literals.", e)

    @classmethod
    def trans_Str(cls, ctx, e, idx):
        raise FragmentError(cls.__name__ + " missing translation method: trans_Str.", cls)

    @classmethod # TODO what are these
    def ana_Bytes(cls, ctx, e, idx):
        raise TyError(cls.__name__ + " does not support byte literals.", e)

    @classmethod
    def trans_Bytes(cls, ctx, e, idx):
        raise FragmentError(cls.__name__ + " missing translation method: trans_Bytes.", cls)

    @classmethod # TODO what are these
    def ana_NameConstant(cls, ctx, e, idx):
        raise TyError(cls.__name__ + " does not support name constant literals.", e)

    @classmethod
    def trans_NameConstant(cls, ctx, e, idx):
        raise FragmentError(cls.__name__ + " missing translation method: trans_NameTyExprstant.", cls)

    @classmethod
    def ana_List(cls, ctx, e, idx):
        raise TyError(cls.__name__ + " does not support list literals.", e)
    
    @classmethod
    def trans_List(cls, ctx, e, idx):
        raise FragmentError(cls.__name__ + " missing translation method: trans_List.", cls)

    @classmethod
    def ana_Tuple(cls, ctx, e, idx):
        raise TyError(cls.__name__ + " does not support tuple literals.", e)
    
    @classmethod
    def trans_Tuple(cls, ctx, e, idx):
        raise FragmentError(cls.__name__ + " missing translation method: trans_Tuple.", e)

    ## 
    ## function def forms
    ## 

    @classmethod
    def syn_FunctionDef(cls, ctx, stmt):
        raise TyError(cls.__name__ + " does not support fragment-decorated def literals.", 
                      stmt)

    @classmethod
    def ana_FunctionDef(cls, ctx, stmt, idx):
        raise TyError(cls.__name__ + " does not support def literals.", stmt)

    @classmethod
    def trans_FunctionDef(cls, ctx, stmt, idx):
        raise FragmentError(cls.__name__ + " missing translation method: trans_FunctionDef.", stmt)


    ## 
    ## other statement forms
    ##

    @classmethod
    def check_Assign(cls, ctx, stmt):
        raise TyError(cls.__name__ + " does not support assignment statements.", cls)

    @classmethod
    def trans_Assign(cls, ctx, stmt):
        raise FragmentError(cls.__name__ + " missing translation method: trans_Assign", cls)

    @classmethod
    def check_Expr(cls, ctx, stmt):
        raise TyError(cls.__name__ + " does not support expression statements.", cls)

    @classmethod
    def trans_Expr(cls, ctx, stmt):
        raise FragmentError(cls.__name__ + " missing translation method: trans_Expr", cls)

    # Targeted Forms
    @classmethod
    def syn_UnaryOp(cls, ctx, e, idx):
        raise TyError(cls.__name__ + " does not support unary operations.", cls)

    @classmethod
    def trans_UnaryOp(cls, ctx, e, idx):
        raise FragmentError(cls.__name__ + " missing translation method: trans_UnaryOp", cls)

    @classmethod
    def syn_IfExp(cls, ctx, e, idx):
        raise TyError(cls.__name__ + " does not support if expressions.", cls)

    @classmethod
    def trans_IfExp(cls, ctx, e, idx):
        raise FragmentError(cls.__name__ + " missing translation method: trans_IfExp", cls)

    @classmethod
    def syn_Call(cls, ctx, e, idx):
        raise TyError(cls.__name__ + " does not support call expressions.", cls)

    @classmethod
    def trans_Call(cls, ctx, e, idx):
        raise FragmentError(cls.__name__ + " missing translation method: trans_Call", cls)

    @classmethod
    def syn_Attribute(cls, ctx, e, idx):
        raise TyError(cls.__name__ + " does not support attribute expressions.", cls)

    @classmethod
    def trans_Attribute(cls, ctx, e, idx):
        raise FragmentError(cls.__name__ + " missing translation method: trans_Attribute", cls)

    @classmethod
    def syn_Subscript(cls, ctx, e, idx):
        raise TyError(cls.__name__ + " does not support subscript expressions.", cls)

    @classmethod
    def trans_Subscript(cls, ctx, e, idx):
        raise FragmentError(cls.__name__ + " missing translation method: trans_Subscript", cls)

    # Binary Forms
    @classmethod
    def syn_BinOp(cls, ctx, e):
        raise TyError(cls.__name__ + " does not support binary operators.", cls)

    @classmethod
    def trans_BinOp(cls, ctx, e):
        raise FragmentError(cls.__name__ + " missing translation method: trans_BinOp.", cls)

def is_fragment(x):
    return inspect.isclass(x) and issubclass(x, Fragment)


