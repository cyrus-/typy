"""Isorecursive types as a library.

Unlike equirecursive types, which typy supports natively, isorecursive
types are not definitionally equal to their unfoldings.

Not sure if these are actually useful for anything, but came up with 
this while thinking about how to do recursive types and its worth having
around for the sake of discussion.

Not complete -- see code comments below.
"""
import typy

_py_fn_class = type(lambda x: x) # could have picked any function

class isorec(typy.Type):
    """Isorecursive types"""
    @classmethod
    def init_idx(cls, idx):
        if not isinstance(idx, _py_fn_class):
            raise typy.TypeFormationError(
                "Index of rec must be a (pure, total) Python function.")
        return idx

    @classmethod
    def init_inc_idx(cls, inc_idx):
        raise typy.TypeFormationError(
            "Cannot construct an incomplete rec type.")

    _unfolded = None

    def unfolded(self):
        _unfolded = self._unfolded
        if _unfolded is None:
            self._unfolded = _unfolded = self.idx(self)
            if _unfolded is self:
                raise typy.TypeFormationError("Invalid unfolding.")
        return _unfolded

    # we just forward all the operations on to the unfolded type
    # note that e.ty afterwards is not equal to the unfolded type!

    def ana_Num(self, ctx, e):
        self.unfolded().ana_Num(ctx, e)

    def translate_Num(self, ctx, e):
        return self.unfolded().translate_Num(ctx, e)

    def ana_pat_Num(self, ctx, pat):
        return self.unfolded().ana_pat(ctx, pat)

    def translate_pat_Num(self, ctx, pat, scrutinee_trans):
        return self.unfolded().translate_pat_Num(ctx, pat, scrutinee_trans)
    
    # TODO: would have to do the same for the analagous methods for other forms

# here are a few py.test tests
import pytest
from typy.std import fn, num, tpl, finsum
from typy.util.testing import translation_eq

def test_rec_type_construction():
    assert isorec[lambda t: num].unfolded() == num
    numlist_idx = lambda t: (finsum['Nil', 'Cons': tpl[num, t]])
    assert isinstance(isorec[numlist_idx], typy.Type)
    numlist = isorec[numlist_idx]
    assert numlist.unfolded() == finsum['Nil', 'Cons': tpl[num, numlist]]

def test_isorecursive():
    assert isorec[lambda t: num] != num

def test_rec_refl():
    idx = lambda t: num
    assert isorec[idx] == isorec[idx]

class TestRecNumIntro:
    @pytest.fixture
    def ty(self):
        return isorec[lambda t: num]

    @pytest.fixture
    def f(self, ty):
        @fn
        def f():
            3 [: ty]
        return f

    def test_type(self, f, ty):
        assert f.typecheck() == fn[(), ty]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 3""")


