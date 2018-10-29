"""Core tests.

To run:
  $ py.test test_core.py
"""
import pytest
import ast

import typy
from typy import component

g = 0
a = 0
def test_component_static_env():
    a = 1
    @component
    def c():
        pass
    assert c.ctx.static_env['g'] == 0
    assert c.ctx.static_env['a'] == 0 # because 'a' is not mentioned in c

def test_component_args():
    with pytest.raises(typy.ComponentFormationError):
        @component
        def c(x):
            pass
    with pytest.raises(typy.ComponentFormationError):
        @component
        def c(*x):
            pass
    with pytest.raises(typy.ComponentFormationError):
        @component
        def c(**x):
            pass

def test_component_unsupported_forms():
    with pytest.raises(typy.ComponentFormationError):
        @component
        def c():
            async def f(): pass
    with pytest.raises(typy.ComponentFormationError):
        @component
        def c():
            class C(): pass
    with pytest.raises(typy.ComponentFormationError):
        @component
        def c():
            return ()
    with pytest.raises(typy.ComponentFormationError):
        @component
        def c():
            import x
    with pytest.raises(typy.ComponentFormationError):
        @component
        def c():
            from x import y
    with pytest.raises(typy.ComponentFormationError):
        @component
        def c():
            global x
    with pytest.raises(typy.ComponentFormationError):
        x = ()
        @component
        def c():
            nonlocal x

def test_component_pass():
    @component
    def c():
        pass

    assert isinstance(c, typy.Component)

from typy.std import unit

def test_component_type_def():
    @component
    def c():
        t [type] = unit
    assert isinstance(c, typy.Component)

def test_component_duplicate_types():
    with pytest.raises(typy.ComponentFormationError):
        @component
        def c():
            t [type] = unit
            t [type] = unit

def test_component_value_member_def():
    @component
    def c():
        x [: unit] = ()
    assert isinstance(c, typy.Component)

def test_component_duplicate_value_members():
    with pytest.raises(typy.ComponentFormationError):
        @component
        def c():
            x [: unit] = ()
            x [: unit] = ()

def test_component_members():
    @component
    def c():
        t [type] = unit
        x [: t] = ()
        y [: t] = x
    
    assert c._module.x == ()
    assert c._module.y == ()

def test_too_many_type_assigns():
    with pytest.raises(typy.ComponentFormationError):
        @component
        def c():
            t [type] = t2 = unit

def test_too_many_val_assigns():
    with pytest.raises(typy.ComponentFormationError):
        @component
        def c():
            t [: unit] = t2 = unit


