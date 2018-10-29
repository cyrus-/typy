import pytest
import ast

from typy import Component, CanonicalType
from typy.std import component, boolean

def test_boolean_intro(self):
    @component
    def c():
        x1 = True [: boolean[()]]
        x2 = False [: boolean[()]]
    assert isinstance(c, Component)
    assert c.values['x1'] == CanonicalType(boolean, ())
    assert c.values['x2'] == CanonicalType(boolean, ())
    
    # TODO: translations

