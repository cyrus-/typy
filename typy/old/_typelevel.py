"""kinds and type expressions"""
import __builtin__

import six

import util
import _inctypes
from _errors import (
    ExtensionError,
    TyError, 
    TypeFormationError, 
    OpNotSupported, 
    OpTranslationLogicMissing)

__all__ = (
    "Kind",
    "T",
    "TyExpr",
    "Type",
    "tycon",
    "is_tycon")

# 
# Kinds
# 

class _KindMetaclass(__builtin__.type):
    def __new__(cls, name, parents, dct):
        # set up cache for each subclass
        dct['_cache'] = {}
        return super(_KindMetaclass, cls).__new__(cls, name, parents, dct)

@six.add_metaclass(_KindMetaclass)
class Kind(object):
    """Kinds"""
    @classmethod
    def __new__(cls, *args, **kwargs):
        # cache lookup
        try:
            return cls._cache[args]
        except KeyError:
            obj = super(Kind, cls).__new__(*args, **kwargs)
            cls._cache[args] = obj
            return obj

    def __repr__(self):
        return str(self)

    def __ne__(self, other):
        return not self.__eq__(other)

class T_(Kind):
    def __str__(self):
        return "T"

    def __eq__(self, other):
        return self is other or isinstance(other, T_)
T = T_() 
"""The kind of types."""

# 
# Type Expressions
# 

class _TyExprMetaclass(__builtin__.type): 
    def __new__(cls, name, parents, dct):
        # set up cache for each subclass
        dct['_cache'] = {}
        return super(_TyExprMetaclass, cls).__new__(
            cls, name, parents, dct)

# list of assumed equivalences (tyexpr1, tyexpr2)
# used while checking type equivalence then cleared
# see Type.__eq__
_eq_assumptions = []
def _in_eq_assumptions(x, y):
    for (a, b) in _eq_assumptions:
        if x is a and y is b:
            return True
    return False

@six.add_metaclass(_TyExprMetaclass)
class TyExpr(object): 
    @classmethod
    def __new__(cls, *args, **kwargs):
        # cache lookup
        try:
            return cls._cache[args]
        except KeyError:
            obj = super(TyExpr, cls).__new__(*args, **kwargs)
            cls._cache[args] = obj
            return obj

    def __repr__(self):
        return str(self)

    def __ne__(self, other):
        return not self.__eq__(other)

    def normalize(self):
        raise ExtensionError(
            "Type expression missing normalization logic.")

class _TypeMetaclass(_TyExprMetaclass):
    def __getitem__(self, idx):
        if util.contains_ellipsis(idx): 
            return _inctypes.IncompleteType._construct_nonrecursive(self, idx)
        else: 
            return Type._construct_nonrecursive(self, idx)

@six.add_metaclass(_TypeMetaclass)
class Type(TyExpr):
    """Base class for typy types."""
    @staticmethod
    def _construct_nonrecursive(tycon, idx, shortname=None):
        idx = tycon.init_idx(idx)
        return tycon(idx, shortname, None, 
                     from_construct_ty=True)

    @staticmethod
    def _construct_equirecursive(tycon, equirec_idx_schema, shortname):
        # first instantiate the instance with the idx == None
        ty = tycon(None, shortname, equirec_idx_schema, 
                   from_construct_ty=True)
        # then pass the instance to the idx schema to get actual idx
        provided_idx_unfolded = equirec_idx_schema(ty)
        # this is initialized by init_idx
        ty.idx = tycon.init_idx(provided_idx_unfolded)
        return ty

    def __init__(self, idx, shortname, equirec_idx_schema, 
                 from_construct_ty=False):
        if not from_construct_ty:
            raise TypeFormationError(
                "Types should not be constructed directly. Use tycon[idx].")
        self.idx = idx
        self.shortname = shortname
        self.equirec_idx_schema = equirec_idx_schema

    def __call__(self, f):
        raise TyError("Non-FnType used as a top-level decorator.")

    def __str__(self):
        shortname = self.shortname
        if self.shortname is not None:
            return shortname
        else:
            return self.anon_to_str()

    def anon_to_str(self):
        return str(self.__class__.__name__) + "[" + str(self.idx) + "]"

    @classmethod
    def anon_inc_to_str(cls, inc_idx):
        return str(cls.__name__) + "[" + str(inc_idx) + "]"

    def __eq__(self, other):
        if self is other:
            return True
        elif _in_eq_assumptions(self, other):
            return True
        else:
            if isinstance(other, Type):
                tycon_self = tycon(self)
                if tycon_self is tycon(other):
                    self_equirec_idx_schema = self.equirec_idx_schema
                    if self_equirec_idx_schema is None:
                        return self.idx == other.idx
                    else:
                        other_equirec_idx_schema = other.equirec_idx_schema
                        if other_equirec_idx_schema is None:
                            return self.idx == other.idx
                        else:
                            self_idx = tycon_self.init_idx(
                                self_equirec_idx_schema(self))
                            other_idx = tycon_self.init_idx(
                                other_equirec_idx_schema(self))
                            return self_idx == other_idx
                else:
                    return False
            elif isinstance(other, TyExpr):
                return other.normalize() == self
            else:
                return False

    def normalize(self):
        return self

    @classmethod
    def init_idx(cls, idx): 
        raise TypeFormationError("init_idx not implemented.")

    @classmethod
    def init_inc_idx(cls, inc_idx):
        raise TypeFormationError("init_inc_idx not implemented.")

    # Num

    def ana_Num(self, ctx, e):
        raise OpNotSupported(self, "method", "ana_Num", 
                             "number literal", e)

    def translate_Num(self, ctx, e):    
        raise OpTranslationLogicMissing(
            self, "method", "translate_Num", 
            "number literal", e)

    @classmethod
    def syn_idx_Num(self, ctx, e, inc_idx):
        raise OpNotSupported(self, "class method", "syn_idx_Num", 
                             "number literal (w/incomplete ascription)", e)

    def ana_pat_Num(self, ctx, pat):
        raise OpNotSupported(self, "method", "ana_pat_Num", 
                             "number literal pattern", pat)

    def translate_pat_Num(self, ctx, pat, scrutinee_trans):
        raise OpTranslationLogicMissing(
            self, "method", "translate_pat_Num",
            "number literal pattern", pat)

    # Str 

    def ana_Str(self, ctx, e):
        raise OpNotSupported(self, "method", "ana_Str", 
                             "string literal", e)

    @classmethod
    def syn_idx_Str(self, ctx, e, inc_idx):
        raise OpNotSupported(self, "class method", "syn_idx_Str", 
                             "string literal (w/incomplete ascription)", e)

    def translate_Str(self, ctx, e):
        raise OpTranslationLogicMissing(
            self, "method", "translate_Str", 
            "string literal", e)

    def ana_pat_Str(self, ctx, pat):
        raise OpNotSupported(self, "method", "ana_pat_Str", 
                             "string literal pattern", pat)

    def translate_pat_Str(self, ctx, pat, scrutinee_trans):
        raise OpTranslationLogicMissing(
            self, "method", "translate_pat_Str", 
            "string literal pattern", pat)

    # Tuple

    def ana_Tuple(self, ctx, e):
        raise OpNotSupported(self, "method", "ana_Tuple", 
                             "tuple", e)

    @classmethod
    def syn_idx_Tuple(self, ctx, e, inc_idx):
        raise OpNotSupported(self, "class method", "syn_idx_Tuple", 
                             "tuple (w/incomplete ascription)", e)

    def translate_Tuple(self, ctx, e):
        raise OpTranslationLogicMissing(
            self, "method", "translate_Tuple", 
            "tuple", e)

    def ana_pat_Tuple(self, ctx, pat):
        raise OpNotSupported(self, "method", "ana_pat_Tuple", pat)

    def translate_pat_Tuple(self, ctx, pat, scrutinee_trans):
        raise OpTranslationLogicMissing(
            self, "method", "translate_pat_Tuple", 
            "tuple pattern", pat)

    # List

    def ana_List(self, ctx, e):
        raise OpNotSupported(self, "method", "ana_List", 
                             "list literal", e)

    @classmethod
    def syn_idx_List(self, ctx, e, inc_idx):
        raise OpNotSupported(self, "class method", "syn_idx_List", 
                             "list literal (w/incomplete ascription)", e)

    def translate_List(self, ctx, e):
        raise OpTranslationLogicMissing(
            self, "method", "translate_List", 
            "list literal", e)

    def ana_pat_List(self, ctx, pat):
        raise OpNotSupported(self, "method", "ana_pat_List", 
                             "list literal pattern", pat)

    def translate_pat_List(self, ctx, pat, scrutinee_trans):
        raise OpTranslationLogicMissing(
            self, "method", "translate_pat_List", 
            "list literal pattern", pat)

    # Dict

    def ana_Dict(self, ctx, e):
        raise OpNotSupported(self, "method", "ana_Dict", 
                             "dict literal", e)

    @classmethod
    def syn_idx_Dict(self, ctx, e, inc_idx):
        raise OpNotSupported(self, "class method", "syn_idx_Dict", 
                             "dict literal (w/incomplete ascription)", e)

    def translate_Dict(self, ctx, e):
        raise OpTranslationLogicMissing(
            self, "method", "translate_Dict", 
            "dict literal", e)

    def ana_pat_Dict(self, ctx, pat):
        raise OpNotSupported(self, "method", "ana_pat_Dict", 
                             "dict literal pattern", pat)

    def translate_pat_Dict(self, ctx, pat, scrutinee_trans):
        raise OpTranslationLogicMissing(
            self, "method", "translate_pat_Dict", 
            "dict literal pattern", pat)

    # Set

    def ana_Set(self, ctx, e):
        raise OpNotSupported(self, "method", "ana_Set", 
                             "set literal", e)

    @classmethod
    def syn_idx_Set(self, ctx, e, inc_idx):
        raise OpNotSupported(self, "class method", "syn_idx_Set", 
                             "set literal (w/incomplete ascription)", e)

    def translate_Set(self, ctx, e):
        raise OpTranslationLogicMissing(
            self, "method", "translate_Set",
            "set literal", e)

    def ana_pat_Set(self, ctx, pat):
        raise OpNotSupported(self, "method", "ana_pat_Set", 
                             "set literal pattern", pat)

    def translate_pat_Set(self, ctx, pat, scrutinee_trans):
        raise OpTranslationLogicMissing(
            self, "method", "translate_pat_Set", 
            "set literal pattern", pat)

    # Lambda

    def ana_Lambda(self, ctx, e):
        raise OpNotSupported(self, "method", "ana_Lambda", 
                             "lambda expression", e)

    @classmethod
    def syn_idx_Lambda(self, ctx, e, inc_idx):
        raise OpNotSupported(self, "class method", "syn_idx_Lambda", 
                             "lambda expression (w/incomplete ascription)", e)

    def translate_Lambda(self, ctx, e):
        raise OpTranslationLogicMissing(
            self, "method", "translate_Lambda", 
            "lambda expression", e)

    # FunctionDef

    def ana_FunctionDef(self, ctx, stmt, ty):
        raise OpNotSupported(self, "method", "ana_FunctionDef", 
                             "definition", stmt)

    @classmethod
    def syn_idx_FunctionDef(cls, ctx, stmt, inc_idx):
        raise OpNotSupported(cls, "class method", "ana_FunctionDef", 
                             "definition (w/incomplete ascription)", stmt)

    def translate_FunctionDef(self, ctx, stmt):
        raise OpTranslationLogicMissing(
            self, "method", "translate_FunctionDef", 
            "definition (w/incomplete ascription)", stmt)

    # Name_constructor
    # TODO: rename these
    # TODO: move this into tydy

    def ana_Name_constructor(self, ctx, e):
        raise OpNotSupported(self, "method", "ana_Name_constructor", 
                             "nullary constructor", e)

    @classmethod
    def syn_idx_Name_constructor(cls, ctx, e, inc_idx):
        raise OpNotSupported(cls, "class method", "syn_idx_Name_constructor", 
                             "nullary constructor (w/incomplete ascription)", e)

    def translate_Name_constructor(self, ctx, e):
        raise OpTranslationLogicMissing(
            self, "method", "translate_Name_constructor",
            "nullary constructor", e)

    def ana_pat_Name_constructor(self, ctx, pat):
        raise OpNotSupported(self, "method", "ana_pat_Name_constructor", 
                             "nullary constructor pattern", pat)

    def translate_pat_Name_constructor(self, ctx, pat, scrutinee_trans):
        raise OpTranslationLogicMissing(
            self, "method", "translate_pat_Name_constructor", 
            "nullary constructor pattern", pat)

    # Unary_Name_constructor
    # TODO: move this into tydy

    def ana_Unary_Name_constructor(self, ctx, e):
        raise OpNotSupported(self, "method", "ana_Unary_Name_constructor", 
                             "unary op + nullary constructor", e)

    @classmethod
    def syn_idx_Unary_Name_constructor(self, ctx, e, inc_idx):
        raise OpNotSupported(self, "class method", "syn_idx_Unary_Name_constructor", 
                             "unary op + nullary constructor (w/incomplete ascription)", e)

    def translate_Unary_Name_constructor(self, ctx, e):
        raise OpTranslationLogicMissing(
            self, "method", "translate_Unary_Name_constructor", 
            "unary op + nullary constructor", e)

    def ana_pat_Unary_Name_constructor(self, ctx, pat):
        raise OpNotSupported(self, "method", "ana_pat_Unary_Name_constructor", 
                             "unary op + nullary constructor pattern", pat)

    def translate_pat_Unary_Name_constructor(self, ctx, pat, scrutinee_trans):
        raise OpTranslationLogicMissing(
            self, "method", "translate_pat_Unary_Name_constructor", 
            "unary op + nullary constructor", pat)

    # Call_constructor
    # TODO: move this into tydy
    # TODO: what about unary call constructors

    def ana_Call_constructor(self, ctx, e):
        raise OpNotSupported(self, "method", "ana_Call_constructor", 
                             "constructor application", e)

    @classmethod
    def syn_idx_Call_constructor(self, ctx, e, inc_idx):
        raise OpNotSupported(self, "method", "syn_idx_Call_constructor", 
                             "constructor application (w/incomplete ascription)", e)

    def translate_Call_constructor(self, ctx, e):
        raise OpTranslationLogicMissing(
            self, "method", "translate_Call_constructor", 
            "constructor application", e)

    def ana_pat_Call_constructor(self, ctx, pat):
        raise OpNotSupported(self, "method", "ana_pat_Call_constructor", 
                             "constructor application pattern", pat)

    def translate_pat_Call_constructor(self, ctx, pat, scrutinee_trans):
        raise OpTranslationLogicMissing(
            self, "method", "translate_pat_Call_constructor", 
            "constructor application pattern", pat)

    # UnaryOp

    def syn_UnaryOp(self, ctx, e):
        raise OpNotSupported(self, "method", "syn_UnaryOp", 
                             "unary operation", e)

    def translate_UnaryOp(self, ctx, e):
        raise OpTranslationLogicMissing(
            self, "method", "translate_UnaryOp", 
            "unary operation", e)

    # BinOp

    def syn_BinOp(self, ctx, e):
        raise OpNotSupported(self, "method", "syn_BinOp", 
                             "binary operation", e)

    def translate_BinOp(self, ctx, e):
        raise OpTranslationLogicMissing(
            self, "method", "translate_BinOp", 
            "binary operation", e)

    # Compare

    def syn_Compare(self, ctx, e):
        raise OpNotSupported(self, "method", "syn_Compare", 
                             "comparison operation", e)

    def translate_Compare(self, ctx, e):
        raise OpTranslationLogicMissing(
            self, "method", "translate_Compare", 
            "comparison operation", e)

    # BoolOp

    def syn_BoolOp(self, ctx, e):
        raise OpNotSupported(self, "method", "syn_BoolOp", 
                             "boolean operation", e)

    def translate_BoolOp(self, ctx, e):
        raise OpTranslationLogicMissing(
            self, "method", "translate_BoolOp", 
            "boolean operation", e)

    # Attribute

    def syn_Attribute(self, ctx, e):
        raise OpNotSupported(self, "method", "syn_Attribute", 
                             "attribute access", e)

    def translate_Attribute(self, ctx, e):
        raise OpTranslationLogicMissing(
            self, "method", "translate_Attribute",
            "attribute access", e)

    # Subscript

    def syn_Subscript(self, ctx, e):
        raise OpNotSupported(self, "method", "syn_Subscript", 
                             "subscript access", e)

    def translate_Subscript(self, ctx, e):
        raise OpTranslationLogicMissing(
            self, "method", "translate_Subscript", 
            "subscript access", e)

    # Call

    def syn_Call(self, ctx, e):
        raise OpNotSupported(self, "method", "syn_Call", 
                             "call", e)

    def translate_Call(self, ctx, e):
        raise OpTranslationLogicMissing(
            self, "method", "translate_Call", 
            "call", e)

def tycon(ty):
    """Returns the tycon of the provided type or incomplete type ."""
    if isinstance(ty, Type):
        return ty.__class__
    elif isinstance(ty, _inctypes.IncompleteType):
        return ty.tycon
    else: # TODO normalization here?
        raise ExtensionError(
            "Argument to tycon is not a type or incomplete type.")

def is_tycon(x):
    """Indicates whether the provided value is a tycon."""
    return issubclass(x, Type)


