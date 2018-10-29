"""py.test based unit tests for typy core

To run:
  $ py.test test_core.py
"""
import pytest
import ast

from typy import (Type, TypeFormationError, tycon, is_tycon, 
                  IncompleteType, FnType, Fn, StaticEnv)

# Test type construction and index validation

class unit_(Type):
    @classmethod
    def init_idx(cls, idx):
        if idx != ():
            raise TypeFormationError("Index of unit type must be ().")
        return idx

unit = unit_[()]

def test_unit_construction(): 
    assert isinstance(unit, Type)

def test_unit_idx():
    assert unit.idx == ()

def test_unit_construction_bad_idx():
    with pytest.raises(TypeFormationError):
        unit_[0]

def test_unit_construction_direct():
    with pytest.raises(TypeError):
        unit_(())

def test_unit_eq():
    assert unit == unit

# Test incomplete type construction and index validation

class ty2_(Type):
    @classmethod
    def init_idx(cls, idx):
        return idx

    @classmethod
    def init_inc_idx(cls, inc_idx):
        if inc_idx is not Ellipsis and inc_idx != (0, Ellipsis):
            raise TypeFormationError("Bad incomplete index.")
        return inc_idx
        
ty2 = ty2_[()]

def test_ty2_eq():
    assert ty2 == ty2
    assert not (ty2 != ty2)

def test_ty2_neq():
    assert ty2 != unit
    assert not (ty2 == unit)

def test_is_tycon():
    assert is_tycon(ty2_) and is_tycon(unit_)

def test_tycon():
    assert tycon(ty2) is ty2_ and tycon(unit) is unit_

def test_incty_construction_1():
    inc_ty2 = ty2_[...]
    assert isinstance(inc_ty2, IncompleteType)
    assert inc_ty2.tycon is ty2_
    assert tycon(inc_ty2) is ty2_
    assert inc_ty2.inc_idx == Ellipsis

def test_incty_construction_2():
    inc_ty2 = ty2_[0, ...]
    assert isinstance(inc_ty2, IncompleteType)
    assert inc_ty2.tycon is ty2_
    assert tycon(inc_ty2) is ty2_
    assert inc_ty2.inc_idx == (0, Ellipsis)

def test_incty_bad_construction():
    with pytest.raises(TypeFormationError):
        ty2_[..., 0]

# Test function type construction

class fn(FnType):
    @classmethod
    def init_idx(cls, idx):
        return idx

    @classmethod
    def init_inc_idx(cls, inc_idx):
        return inc_idx

    def ana_FunctionDef_toplevel(self, ctx, tree): 
        pass
    
    @classmethod
    def syn_idx_FunctionDef_toplevel(self, ctx, tree, inc_ty):
        return (unit, unit)
fnty = fn[unit, unit]

def test_fnty_construction():
    assert isinstance(fnty, FnType)

def test_fnty_decorator():
    @fnty
    def test(): 
        pass
    assert isinstance(test, Fn)
    assert isinstance(test.tree, ast.FunctionDef)

g = 0
a = 0
def test_fnty_static_env():
    a = 1
    
    @fnty
    def test():
        return a
    assert isinstance(test.static_env, StaticEnv)
    assert test.static_env['a'] == 1
    assert test.static_env['g'] == 0

incfnty = fn[...]
def test_incfnty_construction():
    assert isinstance(incfnty, IncompleteType)
    assert tycon(incfnty) == fn

def test_incfnty_decorator():
    @incfnty
    def test():
        pass
    assert isinstance(test, Fn)
    assert test.ascription is incfnty

def test_incfnty_direct_decorator():
    @fn
    def test():
        pass
    assert isinstance(test, Fn)
    assert test.ascription == fn[...]

# see tydy tests for remaining functionality
