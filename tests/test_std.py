"""typy standard library tests"""
import ast

import pytest

import tydy
from tydy import *
from tydy.util.testing import translation_eq

# Type Formation
class TestTypeFormation:
    def test_boolean_index(self):
        with pytest.raises(typy.TypeFormationError):
            boolean_[0]

    def test_stdfn_noargs(self):
        fn_ty = fn[(), unit]
        assert isinstance(fn_ty, typy.Type)
        assert fn_ty.idx == ((), unit)

    def test_stdfn_onearg(self):
        fn_ty = fn[unit, unit]
        assert isinstance(fn_ty, typy.Type)
        assert fn_ty.idx == ((unit,), unit)

    def test_stdfn_twoargs(self):
        fn_ty = fn[unit, unit, unit]
        assert isinstance(fn_ty, typy.Type)
        assert fn_ty.idx == ((unit, unit), unit)

    def test_stdfn_tupled_args(self):
        fn_ty = fn[(unit, unit), unit]
        assert isinstance(fn_ty, typy.Type)
        assert fn_ty.idx == ((unit, unit), unit)

    def test_stdfn_badidx_nottuple(self):
        with pytest.raises(typy.TypeFormationError):
            fn[0]

    def test_stdfn_badidx_nottype(self):
        with pytest.raises(typy.TypeFormationError):
            fn[0, unit]

    def test_stdfn_badidx_nottype2(self):
        with pytest.raises(typy.TypeFormationError):
            fn[(unit, 0), unit]

    def test_stdfn_badidx_rtnottype(self):
        with pytest.raises(typy.TypeFormationError):
            fn[unit, 0]

    def test_stdfn_badidx_too_short(self):
        with pytest.raises(typy.TypeFormationError):
            fn[unit]

    def test_stdfn_incty_construction_all_elided(self):
        fn_incty = fn[...]
        assert isinstance(fn_incty, typy.IncompleteType)
        assert fn_incty.inc_idx == Ellipsis 

    def test_stdfn_incty_construction_noargs_rty_elided(self):
        fn_incty = fn[(), ...]
        assert isinstance(fn_incty, typy.IncompleteType)
        assert fn_incty.inc_idx == ((), Ellipsis)

    def test_stdfn_incty_construction_onearg_rty_elided(self):
        fn_incty = fn[unit, ...]
        assert isinstance(fn_incty, typy.IncompleteType)
        assert fn_incty.inc_idx == ((unit,), Ellipsis)

    def test_stdfn_incty_construction_twoargs_rty_elided(self):
        fn_incty = fn[unit, unit, ...]
        assert isinstance(fn_incty, typy.IncompleteType)
        assert fn_incty.inc_idx == ((unit, unit), Ellipsis)

    def test_stdfn_incty_construction_tupled_args_rty_elided(self):
        fn_incty = fn[(unit, unit), ...]
        assert isinstance(fn_incty, typy.IncompleteType)
        assert fn_incty.inc_idx == ((unit, unit), Ellipsis)

    def test_stdfn_incty_badidx_arg_elided(self):
        with pytest.raises(typy.TypeFormationError):
            fn[..., unit]

    def test_stdfn_incty_badidx_arg_nottuple(self):
        with pytest.raises(typy.TypeFormationError):
            fn[0, ...]

    def test_stdfn_incty_badidx_arg_nottype(self):
        with pytest.raises(typy.TypeFormationError):
            fn[(unit, 0), ...]

# fn

class TestStdFnDirectDecorator:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            pass
        return f

    def test_is_fn(self, f):
        assert isinstance(f, typy.Fn)

    def test_tree(self, f):
        assert isinstance(f.tree, ast.FunctionDef)

def test_stdfn_docstring():
    fnty = fn[unit, unit]
    @fnty
    def f():
        """This is a docstring."""
        pass
    assert f.__doc__ == f.func_doc == """This is a docstring."""

def test_stdfn_incty_docstring():
    @fn
    def f():
        """This is a docstring."""
        pass
    assert f.__doc__ == f.func_doc == """This is a docstring."""

class TestStdFnArgCountCorrect:
    @pytest.fixture
    def fn_ty(self):
        return fn[unit, unit]

    @pytest.fixture
    def f(self, fn_ty):
        @fn_ty
        def f(x):
            """This is a docstring."""
            pass
        return f

    def test_type(self, f, fn_ty):
        assert f.typecheck() == fn_ty

    def test_translate(self, f):
        translation_eq(f, """
            def f(x):
                return ()""")

def test_stdfn_arg_count_incorrect():
    fn_ty = fn[unit, unit]
    @fn_ty
    def test():
        """This is a docstring."""
        pass
    with pytest.raises(tydy.TyError):
        test.typecheck()

class TestStdFnArgCountZero:
    @pytest.fixture
    def fn_ty(self): 
        return fn[(), unit]

    @pytest.fixture
    def f(self, fn_ty):
        @fn_ty
        def f():
            """This is a docstring."""
            pass
        return f

    def test_type(self, f, fn_ty):
        assert f.typecheck() == fn_ty

    def test_translate(self, f):
        translation_eq(f, """
            def f():
                return ()""")

    #def test_eval(self, f):
    #    assert f() == None

def test_stdfn_arg_count_zero_incorrect():
    fn_ty = fn[(), unit]
    @fn_ty
    def f(x):
        """This is a docstring."""
        pass
    with pytest.raises(tydy.TyError):
        f.typecheck()

def test_stdfn_varargs_unsupported():
    fn_ty = fn[unit, unit]
    @fn_ty 
    def f(*x):
        """This is a docstring."""
        pass
    with pytest.raises(tydy.TyError):
        f.typecheck()

def test_stdfn_kwargs_unsupported():
    fn_ty = fn[unit, unit]
    @fn_ty 
    def f(**x):
        """This is a docstring."""
        pass
    with pytest.raises(tydy.TyError):
        f.typecheck()

def test_stdfn_defaults_unsupported():
    fn_ty = fn[unit, unit]
    @fn_ty 
    def f(x=()):
        """This is a docstring."""
        pass
    with pytest.raises(tydy.TyError):
        f.typecheck()

class TestStdFnPass:
    @pytest.fixture
    def fn_ty(self): 
        return fn[(), unit]

    @pytest.fixture
    def f(self, fn_ty):
        @fn_ty
        def f():
            """This is a docstring."""
            pass
        return f

    def test_type(self, fn_ty, f):
        assert f.typecheck() == fn_ty

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return ()""")

    #def test_eval(self, f):
    #    assert f() == None

def test_stdfn_Pass_type():
    fn_ty = fn[(), boolean]
    @fn_ty
    def f():
        pass
    with pytest.raises(typy.TypeMismatchError):
        f.typecheck()

class TestStdFnIncTyEmpty:
    @pytest.fixture
    def f(self):
        fn_ty = fn[(), ...]
        @fn_ty
        def f():
            """This is a docstring."""
            pass
        return f 

    def test_type(self, f):
        assert f.typecheck() == fn[(), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return ()""")

    #def test_eval(self, f):
    #    assert f() == None

class TestStdFnIncTyPass:
    @pytest.fixture
    def f(self):
        fn_ty = fn[(), ...]
        @fn_ty
        def f():
            pass
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return ()""")

    #def test_eval(self, f):
    #    assert f() == None

class TestStdFnSig:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            """This is a docstring."""
            {}
            pass
        return f 

    def test_type(self, f):
        assert f.typecheck() == fn[(), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return ()""")

    #def test_eval(self, f):
    #    assert f() == None

class TestStdFnSigR():
    @pytest.fixture
    def f(self):
        @fn
        def f():
            """This is a docstring."""
            {} >> unit
            pass
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return ()""")

    #def test_eval(self, f):
    #    assert f() == None

class TestStdFnSigPass:
    @pytest.fixture
    def f(self):    
        @fn
        def f():
            """This is a docstring."""
            {}
            pass
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return ()""")

    #def test_eval(self, f):
    #    assert f() == None

class TestStdFnSigRPass:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            """This is a docstring."""
            {} >> unit
            pass
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return ()""")

    #def test_eval(self, f):
    #    assert f() == None

class TestStdFnSigArgs:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {unit}
            pass
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(unit,), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return ()""")

def test_stdfn_sig_args_too_many():
    @fn
    def test(x):
        {unit, unit}
        pass
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_stdfn_sig_args_too_few():
    @fn
    def test(x, y):
        {unit}
        pass
    with pytest.raises(tydy.TyError):
        test.typecheck()

class TestStdFnSigNamedArgs:
    @pytest.fixture 
    def f(self):
        @fn
        def f(x):
            {x : unit}
            pass
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[unit, unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return ()""")

def test_stdfn_sig_named_args_too_many():
    @fn
    def test(x):
        {x : unit, y : unit}
        pass
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_stdfn_sig_named_args_too_few():
    @fn
    def test(x, y):
        {x : unit}
        pass
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_stdfn_sig_named_args_wrong_names():
    @fn
    def test(x):
        {y : unit}
        pass
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_stdfn_sig_named_args_wrong_names2():
    @fn
    def test(x, y):
        {x : unit, z : unit}
        pass
    with pytest.raises(tydy.TyError):
        test.typecheck()

class TestStdFnSigEvalTypes:
    @pytest.fixture
    def f(self):
        q = [unit, boolean]
        @fn
        def f(x, y):
            {x : q[1], y : q[0]} >> q[0]
            pass
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[boolean, unit, unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x, y):
                return ()""")

class TestRedundantSigs:
    @pytest.fixture
    def f(self):
        fn_ty = fn[(), ...]
        @fn_ty 
        def f():
            {}
            pass
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return ()""")

    #def test_eval(self, f):
    #    assert f() == None

class TestRedundantSigs2:
    @pytest.fixture
    def f(self):
        fn_ty = fn[(unit, unit), unit]
        @fn_ty
        def f(x, y):
            {unit, unit} >> unit
            pass
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(unit, unit), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x, y):
                return ()""")

    #def test_eval(self, f):
    #    assert f() == None

class TestRedundantSigs3:
    @pytest.fixture
    def f(self):
        fn_ty = fn[(), ...]
        @fn_ty
        def f():
            {} >> unit
            pass
        return f 

    def test_type(self, f):
        assert f.typecheck() == fn[(), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return ()""")

    #def test_eval(self, f):
    #    assert f() == None

def test_redundant_sigs_4():
    fn_ty = fn[(unit, unit), unit]
    @fn_ty
    def f(x, y):
        {boolean, boolean}
        pass
    with pytest.raises(tydy.TyError):
        f.typecheck()

class TestRedundantSigs5:
    @pytest.fixture
    def f(self):
        fn_ty = fn[(boolean, boolean), unit]
        @fn_ty
        def f(x, y):
            {boolean, boolean}
            pass
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(boolean, boolean), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x, y):
                return ()""")

def test_redundant_sigs_6():
    fn_ty = fn[(unit, unit), ...]
    @fn_ty
    def test(x, y):
        {boolean, unit}
    with pytest.raises(tydy.TyError):
        test.typecheck()

# unit

class TestUnitIntro:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            {} >> unit
            ()
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return ()""")

    #def test_eval(self, f):
    #    assert f() == None

class TestUnitAscription:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            () [: unit]
        return f 

    def test_type(self, f):
        assert f.typecheck() == fn[(), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return ()""")

    #def test_eval(self, f):
    #    assert f() == None 

def test_unit_ascription_toomany():
    @fn
    def test():
        (1, 2) [: unit]
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_unit_bad_ascription():
    @fn
    def test():
        () [: boolean]
    with pytest.raises(typy.NotSupportedError):
        test.typecheck()

def test_unit_bad_inc_ascription():
    @fn
    def test():
        () [: boolean_[...]]
    with pytest.raises(typy.NotSupportedError):
        test.typecheck()

def test_unit_bad_omitted_inc_ascription():
    @fn
    def test():
        () [: boolean_]
    with pytest.raises(typy.NotSupportedError):
        test.typecheck()

class TestSimpleAssign:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x [: unit] = ()
            x
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = ()
                return x""")

class TestSimpleAssignShadow:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x [: unit] = ()
            x [: unit] = ()
            x
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = ()
                __typy_id_x_1__ = ()
                return __typy_id_x_1__""")

class TestSimpleAssignSyn:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x = () [: unit]
            x
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = ()
                return x""")

class TestSimpleAssignSynShadow:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x = () [: unit]
            x = () [: unit]
            x
        return f
    
    def test_type(self, f):
        assert f.typecheck() == fn[(), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = ()
                __typy_id_x_1__ = ()
                return __typy_id_x_1__""")

class TestUnitCompare:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x [: unit] = ()
            x_eq_y = (x == () == ())
            x_eq_y [: boolean]
            x_neq_y = (x != () != ())
            x_neq_y [: boolean]
            x_is_y = (x is () is ())
            x_is_y [: boolean]
            x_isnot_y = (x is not () is not ())
            x_isnot_y [: boolean]
        return f

    def test_type(self, f): 
        assert f.typecheck() == fn[(), boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = ()
                x_eq_y = (x == () == ())
                x_eq_y
                x_neq_y = (x != () != ())
                x_neq_y
                x_is_y = (x is () is ())
                x_is_y
                x_isnot_y = (x is not () is not ())
                return x_isnot_y""")

def test_unit_Lt():
    @fn
    def f():
        x [: unit] = ()
        x < ()
    with pytest.raises(tydy.TyError):
        f.typecheck()

def test_unit_LtE():
    @fn
    def f():
        x [: unit] = ()
        x <= ()
    with pytest.raises(tydy.TyError):
        f.typecheck()

def test_unit_Gt():
    @fn
    def f():
        x [: unit] = ()
        x > ()
    with pytest.raises(tydy.TyError):
        f.typecheck()

def test_unit_GtE():
    @fn
    def f():
        x [: unit] = ()
        x >= ()
    with pytest.raises(tydy.TyError):
        f.typecheck()

def test_unit_In():
    @fn
    def f():
        x [: unit] = ()
        x in ()
    with pytest.raises(tydy.TyError):
        f.typecheck()

def test_unit_NotIn():
    @fn
    def f():
        x [: unit] = ()
        x not in ()
    with pytest.raises(tydy.TyError):
        f.typecheck()

# Variables

class TestVariableLookup:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {x : boolean}
            x
        return f 

    def test_type(self, f):
        assert f.typecheck() == fn[boolean, boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return x""")

class TestVariableLookupAna:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {x : boolean} >> boolean
            x
        return f 

    def test_type(self, f):
        assert f.typecheck() == fn[boolean, boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return x""")

def test_variable_lookup_notfound():
    @fn 
    def test(x):
        {x : boolean}
        y
    with pytest.raises(tydy.TyError):
        test.typecheck()
    
class TestAssignSyn:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x = () [: unit]
            x
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = ()
                return x""")

    #def test_eval(self, f):
    #    assert f() == None

class TestAssignMulti:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x = () [: unit]
            x = () [: unit]
            x
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = ()
                __typy_id_x_1__ = ()
                return __typy_id_x_1__""")

    #def test_eval(self, f):
    #    assert f() == ()

def test_assign_bad():
    @fn
    def test(x):
        {unit}
        x = True [: boolean]  # noqa
    with pytest.raises(tydy.TyError):
        test.typecheck()

class TestAssignAscription:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x [: boolean] = True
            x
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = True
                return x""")

class TestAssignAscriptionShadow:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x [: boolean] = True
            x [: boolean] = True
            x
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = True
                __typy_id_x_1__ = True
                return __typy_id_x_1__""")

class TestAssignShadowDiffTypes:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x [: boolean] = True 
            x [: unit] = ()
            x
        return f
    
    def test_type(self, f):
        assert f.typecheck() == fn[(), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = True
                __typy_id_x_1__ = ()
                return __typy_id_x_1__""")

class TestAssignMultiple:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x [: boolean] = y = True
            y
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = y = True
                return y""")

class TestAssignMultipleAscription:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x [: boolean] = y [: boolean] = True
            y
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = y = True
                return y""")

def test_assign_multiple_ascription_bad():
    @fn
    def test():
        x [: boolean] = y [: unit] = True
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_assign_multiple_ascription_bad_2():
    @fn
    def test(x):
        {x : boolean}
        x [: boolean] = y [: unit] = True
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_assign_multiple_ascription_bad_3():
    @fn
    def test(x):
        {x : unit}
        x [: boolean] = y [: boolean] = True
    with pytest.raises(tydy.TyError):
        test.typecheck()

class TestSimpleLetSyn:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            let [x] = True [: boolean]
            x
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = True
                return x""")
    
class TestSimpleLetAna:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            let [x : boolean] = True
            x
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = True
                return x""")

def test_let_multiple():
    @fn
    def test():
        let [x : boolean] = y = True # noqa
        x
    with pytest.raises(tydy.TyError):
        test.typecheck()

class TestSimpleLetUnderscore:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            let [_ : boolean] = True
            pass
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                True
                return ()""")


class TestSimpleLetUnderscoreSyn:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            let [_] = True [: boolean]
            pass
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                True
                return ()""")

class TestSimpleAssignUnderscore:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            _ = True [: boolean] # noqa
            _ [: boolean] = True
            pass
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                True
                True
                return ()""")

class TestWithBindingSyn:
    @pytest.fixture
    def f(self):
        @fn
        def f(y):
            {num}
            with let[x]:
                y + y
            x
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[num, num]

    def test_translation(self, f):
        translation_eq(f, """
            def f(y):
                __typy_with_scrutinee__ = (y + y)
                x = __typy_with_scrutinee__
                return x""")

class TestWithBindingAna:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            with let[x : num]:
                3
            x + x
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), num]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                __typy_with_scrutinee__ = 3
                x = __typy_with_scrutinee__
                return (x + x)""")

class TestWithBindingSynBlock:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {num}
            with let[(y, z)]:
                y = x + x
                z = x * x
                (y, z) [: tpl]
            y + z
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[num, num]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                y = (x + x)
                z = (x * x)
                __typy_with_scrutinee__ = (y, z)
                __typy_id_y_1__ = __typy_with_scrutinee__[0]
                __typy_id_z_1__ = __typy_with_scrutinee__[1]
                return (__typy_id_y_1__ + __typy_id_z_1__)""")

class TestWithBindingNested:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {num}
            with let[y]:
                with let[z]:
                    x + x
                z * z
            y - y
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[num, num]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                __typy_with_scrutinee__ = (x + x)
                z = __typy_with_scrutinee__
                __typy_with_scrutinee__ = (z * z)
                y = __typy_with_scrutinee__
                return (y - y)""")

def test_with_binding_block_local():
    @fn
    def f(x):
        {num}
        with let[q]:
            y = x + x
            z = x * x
            y + z
        y + z
    with pytest.raises(tydy.TyError):
        f.typecheck()

class TestRecursiveFn:
    @pytest.fixture
    def f(self):
        @fn
        def f(x, y):
            {boolean, boolean} >> boolean
            f(x, y)
        return f 

    def test_type(self, f):
        assert f.typecheck() == fn[(boolean, boolean), boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x, y):
                return f(x, y)""")

def test_nonrecursive_fn():
    @fn
    def f():
        {}
        f()
    with pytest.raises(tydy.TyError):
        f.typecheck()

class TestShadowFnName: 
    @pytest.fixture
    def f(self):
        @fn
        def f(f):
            {boolean} >> boolean
            f
        return f
     
    def test_type(self, f):
        assert f.typecheck() == fn[boolean, boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f(__typy_id_f_1__):
                return __typy_id_f_1__""")

class TestAssignFnName:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {boolean} >> boolean
            f(x) # noqa
            f = x
            f
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[boolean, boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                f(x)
                __typy_id_f_1__ = x
                return __typy_id_f_1__""")

# 
# fn
# 
class TestAnaLambda:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x [: fn[num, num]] = lambda x: 3
            x
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), fn[num, num]]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                __typy_id_x_1__ = (lambda x: 3)
                return __typy_id_x_1__""")

class TestAnaFunctionDef:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            {} >> fn[num, num]
            with let[z : fn[num, num]]:
                def f1(x):
                    x [: num]
                    3
            def f(x):
                x [: num]
                3
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), fn[num, num]]

    def test_translation(self, f):
        translation_eq(f, """
            def f():

                def f1(x):
                    x
                    return 3
                __typy_with_scrutinee__ = f1
                z = __typy_with_scrutinee__

                def __typy_id_f_1__(__typy_id_x_1__):
                    __typy_id_x_1__
                    return 3
                return __typy_id_f_1__""")

class TestSynLambda:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x [: fn[num, ...]] = lambda x: x + 3
            x
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), fn[num, num]]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                __typy_id_x_1__ = (lambda x: (x + 3))
                return __typy_id_x_1__""")

class TestSynFunctionDef:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            with let[f2]:
                @fn
                def f1(x):
                    {num}
                    x + 1
            f2 [: fn[num, num]]
            @fn
            def f3(y):
                {num}
                y + 1
            f3 [: fn[num, num]]
            @fn
            def f4(z):
                {num}
                f2(z) + f3(z)
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), fn[num, num]]

    def test_translation(self, f):
        translation_eq(f, """
            def f():

                def f1(x):
                    return (x + 1)
                __typy_with_scrutinee__ = f1
                f2 = __typy_with_scrutinee__
                f2

                def f3(y):
                    return (y + 1)
                f3
                
                def f4(z):
                    return (f2(z) + f3(z))
                return f4""")

class TestLambdaNoArgs:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x [: fn[(), num]] = lambda: 3
            (lambda: x) [: fn]
        return f
    
    def test_type(self, f):
        assert f.typecheck() == fn[(), fn[(), fn[(), num]]]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = (lambda : 3)
                return (lambda : x)""")

#
# boolean
#

from tydy.core._boolean import boolean_

class TestBooleanAscriptionTrue:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            True [: boolean]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return True""")

class TestBooleanAscriptionFalse:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            False [: boolean]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return False""")

class TestBooleanIncAscription:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            True [: boolean_]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return True""")

def test_boolean_ascription_bad():
    @fn
    def test():
        Bad [: boolean]
    with pytest.raises(tydy.TyError):
        test.typecheck()

class TestBooleanNot:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x [: boolean] = True
            not x
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = True
                return (not x)""")

def test_boolean_Invert():
    @fn
    def test():
        x [: boolean] = True
        ~x
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_boolean_UAdd():
    @fn
    def test():
        x [: boolean] = True
        +x
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_boolean_USub():
    @fn
    def test():
        x [: boolean] = True
        -x
    with pytest.raises(tydy.TyError):
        test.typecheck()

class TestBooleanCompareOps:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x [: boolean] = True
            x_eq_y = (x == True) # noqa
            x_eq_y [: boolean]
            x_neq_y = (x != True) # noqa
            x_neq_y [: boolean]
            x_is_y = (x is True)
            x_is_y [: boolean]
            x_isnot_y = (x is not True)
            x_isnot_y
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = True
                x_eq_y = (x == True)
                x_eq_y
                x_neq_y = (x != True)
                x_neq_y
                x_is_y = (x is True)
                x_is_y
                x_isnot_y = (x is not True)
                return x_isnot_y""")

def test_boolean_Lt():
    @fn
    def test():
        x [: boolean] = True
        y [: boolean] = False
        x < y
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_boolean_LtE():
    @fn
    def test():
        x [: boolean] = True
        y [: boolean] = False
        x <= y
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_boolean_Gt():
    @fn
    def test():
        x [: boolean] = True
        y [: boolean] = False
        x > y
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_boolean_GtE():
    @fn
    def test():
        x [: boolean] = True
        y [: boolean] = False
        x >= y
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_boolean_In():
    @fn
    def test():
        x [: boolean] = True
        y [: boolean] = False
        x in y
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_boolean_NotIn():
    @fn
    def test():
        x [: boolean] = True
        y [: boolean] = False
        x not in y
    with pytest.raises(tydy.TyError):
        test.typecheck()

class TestBooleanBoolOps:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x [: boolean] = True
            x_and_y = (x and True and True and True)
            x_and_y [: boolean]
            x_or_y = (x or True or True or True)
            x_or_y [: boolean]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = True
                x_and_y = (x and True and True and True)
                x_and_y
                x_or_y = (x or True or True or True)
                return x_or_y""")

class TestBooleanBlockIf:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {boolean} >> num
            if x:
                x
            elif x and x:
                not x
            else:
                not not x
            with let[y : boolean]:
                if x:
                    False
                elif x and x:
                    True
                else:
                    True
            if y:
                4
            elif x and y:
                5
            else:
                6
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[boolean, num]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                if x:
                    x
                elif (x and x):
                    (not x)
                else:
                    (not (not x))
                if x:
                    __typy_with_scrutinee__ = False
                elif (x and x):
                    __typy_with_scrutinee__ = True
                else:
                    __typy_with_scrutinee__ = True
                y = __typy_with_scrutinee__
                if y:
                    return 4
                elif (x and y):
                    return 5
                else:
                    return 6""")

class TestBooleanIfExp:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {boolean} >> num
            x if x else not x if x and x else not not x
            y = (False if x else True if x and x else True) [: boolean]
            4 if y else 5 if x and y else 6
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[boolean, num]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                (x if x else ((not x) if (x and x) else (not (not x))))
                y = (False if x else (True if (x and x) else True))
                return (4 if y else (5 if (x and y) else 6))""")

# 
# num
#

from tydy.core._numeric import num_

class TestIntegerIntro:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            3 [: num]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), num]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 3""")

class TestIntegerIncIntro:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            3 [: num_]
        return f 

    def test_type(self, f):
        assert f.typecheck() == fn[(), num]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 3""")

class TestIntegerLongIntro:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            1234567890123456789012345678901234567890123456789012345678901234567890 [: num]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), num]

    def test_translation(self, f):  
        translation_eq(f, """
            def f():
                return 1234567890123456789012345678901234567890123456789012345678901234567890L""")

def test_Integer_ascription_on_ieee():
    @fn
    def test():
        3.0 [: num]
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_Integer_ascription_on_cplx():
    @fn
    def test():
        3.0j [: num]
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_Integer_ascription_on_stringing():
    @fn
    def test():
        "3" [: num]
    with pytest.raises(tydy.TyError):
        test.typecheck()

class TestIntegerUnaryOps:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x = 123 [: num]
            x_plus = +x
            x_plus [: num]
            x_minus = -x
            x_minus [: num]
            x_invert = ~x
            x_invert [: num]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), num]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = 123
                x_plus = (+ x)
                x_plus
                x_minus = (- x)
                x_minus
                x_invert = (~ x)
                return x_invert""")

def test_Integer_no_not():
    @fn
    def test():
        not (3 [: num])
    with pytest.raises(tydy.TyError):
        test.typecheck()

class TestIntegerBinops:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x = 123 [: num]
            y = 456 [: num]
            x_plus_y = x + y
            x_plus_y [: num]
            x_minus_y = x - y
            x_minus_y [: num]
            x_mult_y = x * y
            x_mult_y [: num]
            x_mod_y = x % y
            x_mod_y [: num]
            x_pow_y = x ** y
            x_pow_y [: num]
            x_lshift_y = x << y
            x_lshift_y [: num]
            x_rshift_y = x >> y
            x_rshift_y [: num]
            x_bitor_y = x | y
            x_bitor_y [: num]
            x_bitxor_y = x ^ y
            x_bitxor_y [: num]
            x_bitand_y = x & y
            x_bitand_y [: num]
            x_floordiv_y = x // y
            x_floordiv_y [: num]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), num]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = 123
                y = 456
                x_plus_y = (x + y)
                x_plus_y
                x_minus_y = (x - y)
                x_minus_y
                x_mult_y = (x * y)
                x_mult_y
                x_mod_y = (x % y)
                x_mod_y
                x_pow_y = (x ** y)
                x_pow_y
                x_lshift_y = (x << y)
                x_lshift_y
                x_rshift_y = (x >> y)
                x_rshift_y
                x_bitor_y = (x | y)
                x_bitor_y
                x_bitxor_y = (x ^ y)
                x_bitxor_y
                x_bitand_y = (x & y)
                x_bitand_y
                x_floordiv_y = (x // y)
                return x_floordiv_y""")

# see TestnumieeeDiv for Integer/ieee division
def test_Integer_num_div():
    @fn
    def test():
        x [: num] = 3
        x / x
    with pytest.raises(tydy.TyError):
        test.typecheck()

class TestIntegerCompareOps:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x = 123 [: num]
            x_eq_y = (x == 456 == 789)
            x_eq_y [: boolean]
            x_neq_y = (x != 456 != 789)
            x_neq_y [: boolean]
            x_lt_y = (x < 456 < 789)
            x_lt_y [: boolean]
            x_lte_y = (x <= 456 <= 789)
            x_lte_y [: boolean]
            x_gt_y = (x > 456 > 789)
            x_gt_y [: boolean]
            x_gte_y = (x >= 456 >= 789)
            x_gte_y [: boolean]
            x_is_y = (x is 456 is 789)
            x_is_y [: boolean]
            x_isnot_y = (x is not 456 is not 789) 
            x_isnot_y [: boolean]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = 123
                x_eq_y = (x == 456 == 789)
                x_eq_y
                x_neq_y = (x != 456 != 789)
                x_neq_y
                x_lt_y = (x < 456 < 789)
                x_lt_y
                x_lte_y = (x <= 456 <= 789)
                x_lte_y
                x_gt_y = (x > 456 > 789)
                x_gt_y
                x_gte_y = (x >= 456 >= 789)
                x_gte_y
                x_is_y = (x is 456 is 789)
                x_is_y
                x_isnot_y = (x is not 456 is not 789)
                return x_isnot_y""")

def test_num_In():
    @fn
    def test():
        x [: num] = 123
        y [: num] = 456
        x in y
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_num_NotIn():
    @fn
    def test():
        x [: num] = 123
        y [: num] = 456
        x not in y
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_num_And():
    @fn
    def test():
        x [: num] = 123
        y [: num] = 456
        x and y
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_num_Or():
    @fn
    def test():
        x [: num] = 123
        y [: num] = 456
        x or y
    with pytest.raises(tydy.TyError):
        test.typecheck()

#
# ieee
#

from tydy.core._numeric import ieee_

class TestIEEEIntroF:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            3.0 [: ieee]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), ieee]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 3.0""")

class TestIEEEIntroI:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            3 [: ieee]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), ieee]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 3.0""")

class TestIEEEIntroL:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            1234567890123456789012345678901234567890123456789012345678901234567890 [: ieee]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), ieee]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 1.2345678901234567e+69""")

class TestIEEEIntroName:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x1 = Inf [: ieee]
            x1 [: ieee]
            x2 = NaN [: ieee]
            x2 [: ieee]
            x3 = Inf [: ieee_]
            x3 [: ieee]
            x4 = NaN [: ieee_]
            x4 [: ieee]
            x5 [: ieee] = -Inf
            x5 [: ieee]
            x6 [: ieee] = +Inf
            x6 [: ieee]
            x7 [: ieee_] = -Inf
            x7 [: ieee]
            x8 [: ieee_] = +Inf
            x8 [: ieee]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), ieee]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x1 = __builtin__.float('Inf')
                x1
                x2 = __builtin__.float('NaN')
                x2
                x3 = __builtin__.float('Inf')
                x3
                x4 = __builtin__.float('NaN')
                x4
                x5 = __builtin__.float('-Inf')
                x5
                x6 = __builtin__.float('Inf')
                x6
                x7 = __builtin__.float('-Inf')
                x7
                x8 = __builtin__.float('Inf')
                return x8""")

class TestIntegerIncIntroF:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            3.0 [: ieee_]
        return f 

    def test_type(self, f):
        assert f.typecheck() == fn[(), ieee]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 3.0""")

class TestIntegerIncIntroI:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            3 [: ieee_]
        return f 

    def test_type(self, f):
        assert f.typecheck() == fn[(), ieee]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 3.0""")

class TestIEEEIncIntroL:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            1234567890123456789012345678901234567890123456789012345678901234567890 [: ieee_]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), ieee]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 1.2345678901234567e+69""")

def test_ieee_ascription_on_cplx():
    @fn
    def test():
        3.0j [: ieee]
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_ieee_ascription_on_stringing():
    @fn
    def test():
        "3" [: ieee]
    with pytest.raises(tydy.TyError):
        test.typecheck()

class TestIEEEUnaryOps:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x = 123 [: ieee]
            x_plus = +x
            x_plus [: ieee]
            x_minus = -x
            x_minus [: ieee]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), ieee]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = 123.0
                x_plus = (+ x)
                x_plus
                x_minus = (- x)
                return x_minus""")

def test_ieee_no_not():
    @fn
    def test():
        not (3 [: ieee])
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_ieee_no_invert():
    @fn
    def test():
        x [: ieee] = 3
        ~x
    with pytest.raises(tydy.TyError):
        test.typecheck()

class TestIEEEBinops:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x = 123 [: ieee]
            y = 456 [: ieee]
            x_plus_y = x + y
            x_plus_y [: ieee]
            x_minus_y = x - y
            x_minus_y [: ieee]
            x_mult_y = x * y
            x_mult_y [: ieee]
            x_mod_y = x % y
            x_mod_y [: ieee]
            x_pow_y = x ** y
            x_pow_y [: ieee]
            x_div_y = x / y
            x_div_y [: ieee]
            x_floordiv_y = x // y
            x_floordiv_y [: ieee]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), ieee]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = 123.0
                y = 456.0
                x_plus_y = (x + y)
                x_plus_y
                x_minus_y = (x - y)
                x_minus_y
                x_mult_y = (x * y)
                x_mult_y
                x_mod_y = (x % y)
                x_mod_y
                x_pow_y = (x ** y)
                x_pow_y
                x_div_y = (x / y)
                x_div_y
                x_floordiv_y = (x // y)
                return x_floordiv_y""")

def test_ieee_no_lshift():
    @fn
    def test():
        x [: ieee] = 3
        x << x
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_ieee_no_rshift():
    @fn
    def test():
        x [: ieee] = 3
        x >> x
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_ieee_no_bitor():
    @fn
    def test():
        x [: ieee] = 3
        x | x
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_ieee_no_bitxor():
    @fn
    def test():
        x [: ieee] = 3
        x ^ x
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_ieee_no_bitand():
    @fn
    def test():
        x [: ieee] = 3
        x & x
    with pytest.raises(tydy.TyError):
        test.typecheck()
 
class TestIEEECompareOps:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x = 123 [: ieee]
            x_eq_y = (x == 456 == 789)
            x_eq_y [: boolean]
            x_neq_y = (x != 456 != 789)
            x_neq_y [: boolean]
            x_lt_y = (x < 456 < 789)
            x_lt_y [: boolean]
            x_lte_y = (x <= 456 <= 789)
            x_lte_y [: boolean]
            x_gt_y = (x > 456 > 789)
            x_gt_y [: boolean]
            x_gte_y = (x >= 456 >= 789)
            x_gte_y [: boolean]
            x_is_y = (x is 456 is 789)
            x_is_y [: boolean]
            x_isnot_y = (x is not 456 is not 789) 
            x_isnot_y [: boolean]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = 123.0
                x_eq_y = (x == 456.0 == 789.0)
                x_eq_y
                x_neq_y = (x != 456.0 != 789.0)
                x_neq_y
                x_lt_y = (x < 456.0 < 789.0)
                x_lt_y
                x_lte_y = (x <= 456.0 <= 789.0)
                x_lte_y
                x_gt_y = (x > 456.0 > 789.0)
                x_gt_y
                x_gte_y = (x >= 456.0 >= 789.0)
                x_gte_y
                x_is_y = (x is 456.0 is 789.0)
                x_is_y
                x_isnot_y = (x is not 456.0 is not 789.0)
                return x_isnot_y""")

def test_ieee_In():
    @fn
    def test():
        x [: ieee] = 123
        y [: ieee] = 456
        x in y
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_ieee_NotIn():
    @fn
    def test():
        x [: ieee] = 123
        y [: ieee] = 456
        x not in y
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_ieee_And():
    @fn
    def test():
        x [: ieee] = 123
        y [: ieee] = 456
        x and y
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_ieee_Or():
    @fn
    def test():
        x [: ieee] = 123
        y [: ieee] = 456
        x or y
    with pytest.raises(tydy.TyError):
        test.typecheck()

class TestNumIEEEDiv:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x [: num] = 3
            x / 2
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), ieee]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = 3
                return (x / 2.0)""")

#
# cplx
#

from tydy.core._numeric import cplx_

class TestcplxIntroI:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            3 [: cplx]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), cplx]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return (3+0j)""")

class TestcplxIntroF:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            3.0 [: cplx]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), cplx]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return (3+0j)""")

class TestcplxIntroL:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            1234567890123456789012345678901234567890123456789012345678901234567890 [: cplx]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), cplx]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return (1.2345678901234567e+69+0j)""")

class TestcplxIntroC:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            3j [: cplx]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), cplx]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 3j""")

class TestcplxIncIntroI:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            3 [: cplx_]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), cplx]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return (3+0j)""")

class TestcplxIncIntroF:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            3.0 [: cplx_]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), cplx]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return (3+0j)""")

class TestcplxIncIntroL:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            1234567890123456789012345678901234567890123456789012345678901234567890 [: cplx_]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), cplx]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return (1.2345678901234567e+69+0j)""")

class TestcplxIncIntroC:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            3j [: cplx_]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), cplx]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 3j""")

def test_cplx_Intro_tuple_short():
    @fn
    def f():
        (0,) [: cplx]
    with pytest.raises(tydy.TyError):
        f.typecheck()

def test_cplx_Intro_tuple_long():
    @fn
    def f():
        (0, 0, 0) [: cplx]
    with pytest.raises(tydy.TyError):
        f.typecheck()

class TestcplxIntroTuple:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            (1, 0) [: cplx] # II
            (1, 0) [: cplx_]
            (2.0, 3) [: cplx] # FI
            (2.0, 3) [: cplx_]
            (3.0, 3.0) [: cplx] # FF
            (3.0, 3.0) [: cplx_]
            (4, 3j) [: cplx] # IC
            (4, 3j) [: cplx_]
            x [: num] = 1
            (x, 5) [: cplx]
            (x, 6) [: cplx_]
            (7, x) [: cplx]
            (8, x) [: cplx_]
            y [: ieee] = 1
            (y, 9) [: cplx]
            (y, 10) [: cplx_]
            (11, y) [: cplx]
            (12, y) [: cplx_]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), cplx]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                __builtin__.complex(1.0, 0)
                __builtin__.complex(1.0, 0)
                __builtin__.complex(2.0, 3)
                __builtin__.complex(2.0, 3)
                __builtin__.complex(3.0, 3.0)
                __builtin__.complex(3.0, 3.0)
                __builtin__.complex(4.0, 3.0)
                __builtin__.complex(4.0, 3.0)
                x = 1
                __builtin__.complex(x, 5)
                __builtin__.complex(x, 6)
                __builtin__.complex(7.0, x)
                __builtin__.complex(8.0, x)
                y = 1.0
                __builtin__.complex(y, 9)
                __builtin__.complex(y, 10)
                __builtin__.complex(11.0, y)
                return __builtin__.complex(12.0, y)""")

def test_cplx_Intro_tuple_rl_bad():
    @fn
    def f():
        x [: boolean] = True
        (x, 0) [: cplx]
    with pytest.raises(tydy.TyError):
        f.typecheck()

def test_cplx_Intro_tuple_im_bad():
    @fn
    def f():
        x [: boolean] = True
        (0, x) [: cplx]
    with pytest.raises(tydy.TyError):
        f.typecheck()

def test_cplx_ascription_on_stringing():
    @fn
    def test():
        "3" [: cplx]
    with pytest.raises(tydy.TyError):
        test.typecheck()

class TestcplxUnaryOps:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x = 123 [: cplx]
            x_plus = +x
            x_plus [: cplx]
            x_minus = -x
            x_minus [: cplx]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), cplx]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = (123+0j)
                x_plus = (+ x)
                x_plus
                x_minus = (- x)
                return x_minus""")

def test_cplx_no_not():
    @fn
    def test():
        not (3 [: cplx])
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_cplx_no_invert():
    @fn
    def test():
        x [: cplx] = 3
        ~x
    with pytest.raises(tydy.TyError):
        test.typecheck()

class TestIEEEBinopsCC:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x = 123 [: cplx]
            y = 456 [: cplx]
            x_plus_y = x + y
            x_plus_y [: cplx]
            x_minus_y = x - y
            x_minus_y [: cplx]
            x_mult_y = x * y
            x_mult_y [: cplx]
            x_pow_y = x ** y
            x_pow_y [: cplx]
            x_div_y = x / y
            x_div_y [: cplx]
            x_floordiv_y = x // y
            x_floordiv_y [: cplx]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), cplx]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = (123+0j)
                y = (456+0j)
                x_plus_y = (x + y)
                x_plus_y
                x_minus_y = (x - y)
                x_minus_y
                x_mult_y = (x * y)
                x_mult_y
                x_pow_y = (x ** y)
                x_pow_y
                x_div_y = (x / y)
                x_div_y
                x_floordiv_y = (x // y)
                return x_floordiv_y""")

def test_cplx_no_mod():
    @fn
    def test():
        x [: cplx] = 3
        x % x
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_cplx_no_lshift():
    @fn
    def test():
        x [: cplx] = 3
        x << x
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_cplx_no_rshift():
    @fn
    def test():
        x [: cplx] = 3
        x >> x
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_cplx_no_bitor():
    @fn
    def test():
        x [: cplx] = 3
        x | x
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_cplx_no_bitxor():
    @fn
    def test():
        x [: cplx] = 3
        x ^ x
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_cplx_no_bitand():
    @fn
    def test():
        x [: cplx] = 3
        x & x
    with pytest.raises(tydy.TyError):
        test.typecheck()
 
class TestcplxCompareOps:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x = 123 [: cplx]
            x_eq_y = (x == 456 == 789)
            x_eq_y [: boolean]
            x_neq_y = (x != 456 != 789)
            x_neq_y [: boolean]
            x_is_y = (x is 456 is 789)
            x_is_y [: boolean]
            x_isnot_y = (x is not 456 is not 789) 
            x_isnot_y [: boolean]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = (123+0j)
                x_eq_y = (x == (456+0j) == (789+0j))
                x_eq_y
                x_neq_y = (x != (456+0j) != (789+0j))
                x_neq_y
                x_is_y = (x is (456+0j) is (789+0j))
                x_is_y
                x_isnot_y = (x is not (456+0j) is not (789+0j))
                return x_isnot_y""")

def test_cplx_Lt():
    @fn
    def test():
        x [: cplx] = 123
        y [: cplx] = 456
        x < y
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_cplx_LtE():
    @fn
    def test():
        x [: cplx] = 123
        y [: cplx] = 456
        x <= y
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_cplx_Gt():
    @fn
    def test():
        x [: cplx] = 123
        y [: cplx] = 456
        x > y
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_cplx_GtE():
    @fn
    def test():
        x [: cplx] = 123
        y [: cplx] = 456
        x >= y
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_cplx_In():
    @fn
    def test():
        x [: cplx] = 123
        y [: cplx] = 456
        x in y
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_cplx_NotIn():
    @fn
    def test():
        x [: cplx] = 123
        y [: cplx] = 456
        x not in y
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_cplx_And():
    @fn
    def test():
        x [: cplx] = 123
        y [: cplx] = 456
        x and y
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_cplx_Or():
    @fn
    def test():
        x [: cplx] = 123
        y [: cplx] = 456
        x or y
    with pytest.raises(tydy.TyError):
        test.typecheck()

class TestcplxComponents():
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x [: cplx] = 456
            r [: ieee] = x.real
            x.imag
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), ieee]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = (456+0j)
                r = x.real
                return x.imag""")

class TestcplxConjugate():
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x [: cplx] = 456
            x.conjugate()
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), cplx]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = (456+0j)
                return x.conjugate()""")

# 
# conversions
#

class TestConvertIF():
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x [: num] = 456
            x.f
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), ieee]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = 456
                return __builtin__.float(x)""")

class TestConvertIC():
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x [: num] = 456
            x.c
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), cplx]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = 456
                return __builtin__.complex(x)""")

class TestConvertFC():
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x [: ieee] = 456
            x.c
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), cplx]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = 456.0
                return __builtin__.complex(x)""")

#
# string
# 

from tydy.core._string import string_

class TestStringIntro:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            "test" [: string]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), string]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 'test'""")

class TestStringIncIntro:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            "test" [: string_]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), string]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 'test'""")

def test_string_num_Intro():
    @fn
    def test(self):
        123 [: string]
    with pytest.raises(tydy.TyError):
        test.typecheck()

class TestStringAdd:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            ("test" [: string]) + "test"
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), string]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return ('test' + 'test')""")

class TestStringCompare:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x1 = "abc" [: string] == "def" == "ghi"
            x1 [: boolean]
            x2 = "abc" [: string] != "def" != "ghi"
            x2 [: boolean]
            x3 = "abc" [: string] is "def" is "ghi"
            x3 [: boolean]
            x4 = "abc" [: string] is not "def" is not "ghi" 
            x4 [: boolean]
            x5 = "abc" [: string] in "def" in "ghi"
            x5 [: boolean]
            x6 = "abc" [: string] not in "def" not in "ghi"
            x6 [: boolean]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x1 = ('abc' == 'def' == 'ghi')
                x1
                x2 = ('abc' != 'def' != 'ghi')
                x2
                x3 = ('abc' is 'def' is 'ghi')
                x3
                x4 = ('abc' is not 'def' is not 'ghi')
                x4
                x5 = ('abc' in 'def' in 'ghi')
                x5
                x6 = ('abc' not in 'def' not in 'ghi')
                return x6""") 

class TestStringSubscript:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x [: string] = "abcdefg"
            y1 = x[0]
            y1 [: string]
            y2 = x[0:1]
            y2 [: string]
            y3 = x[0:1:2]
            y3 [: string]
            y4 = x[0:]
            y4 [: string]
            # no x[:1] because that's ascription syntax
            # can always use x[0:1] for this
            y5 = x[0:1:]
            y5 [: string]
            y6 = x[0::1]
            y6 [: string]
            y7 = x[:0:1]
            y7 [: string]
            y8 = x[0::]
            y8 [: string]
            y9 = x[:0:]
            y9 [: string]
            y10 = x[::0]
            y10 [: string]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), string]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = 'abcdefg'
                y1 = x[0]
                y1
                y2 = x[0:1]
                y2
                y3 = x[0:1:2]
                y3
                y4 = x[0:]
                y4
                y5 = x[0:1]
                y5
                y6 = x[0::1]
                y6
                y7 = x[:0:1]
                y7
                y8 = x[0:]
                y8
                y9 = x[:0]
                y9
                y10 = x[::0]
                return y10""")

# 
# tpl
#

import typy.util
odict = typy.util.odict

def test_tpl_formation_unit():
    assert isinstance(tpl[()], typy.Type)
    assert tpl[()].idx == odict(())

def test_tpl_formation_single_ty():
    assert isinstance(tpl[num], typy.Type)
    assert tpl[num].idx == odict((
        (0, num),
    ))

def test_tpl_formation_two_ty():
    assert isinstance(tpl[num, num], typy.Type)
    assert tpl[num, num].idx == odict((
        (0, num),
        (1, num)
    ))

def test_tpl_formation_single_noty():
    with pytest.raises(typy.TypeFormationError):
        tpl["num"]

def test_tpl_formation_two_noty():
    with pytest.raises(typy.TypeFormationError):
        tpl[num, "num"]

def test_tpl_formation_single_label():
    assert tpl["lbl0" : num].idx == odict((
        ("lbl0", num),
    ))

def test_tpl_formation_two_labels():
    assert tpl["lbl0": num, "lbl1": string].idx == odict((
        ("lbl0", num),
        ("lbl1", string)
    ))

def test_tpl_formation_duplicate_labels():
    with pytest.raises(typy.TypeFormationError):
        tpl["lbl0": num, "lbl0": string]

def test_tpl_formation_empty_lbl():
    with pytest.raises(typy.TypeFormationError):
        tpl["": num]

def test_tpl_formation_num_labels():
    assert tpl[1 : num, 0 : num].idx == odict((
        (1, num),
        (0, num)
    ))

def test_tpl_formation_neg_label():
    with pytest.raises(typy.TypeFormationError):
        tpl[-1 : num]

def test_tpl_formation_non_stringing_label():
    with pytest.raises(typy.TypeFormationError):
        tpl[None : num]

def test_tpl_formation_non_type_component():
    with pytest.raises(typy.TypeFormationError):
        tpl["lbl0" : None]

def test_tpl_inc_ty_formation():
    assert isinstance(tpl[...], typy.IncompleteType)

def test_tpl_inc_ty_formation_bad():
    with pytest.raises(typy.TypeFormationError):
        tpl[..., 'lbl0' : num]

class TestTplTupleIntroUnit:
    @pytest.fixture
    def f(self):
        @fn 
        def f():
            () [: tpl[()]]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), tpl[()]]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return ()""")

class TestTplTupleIncIntroUnit:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            () [: tpl]
        return f 

    def test_type(self, f):
        assert f.typecheck() == fn[(), tpl[()]]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return ()""")

class TestTplTupleIntro:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x [: string] = "test"
            y [: num] = 0
            z1 [: tpl[string]] = (x,)
            z2 [: tpl[string, num]] = (x, y)
            z3 [: tpl['lbl0': string]] = (x,)
            z4 [: tpl['lbl0': string, 'lbl1': num]] = (x, y)
            z4
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), tpl['lbl0': string, 'lbl1': num]]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = 'test'
                y = 0
                z1 = (x,)
                z2 = (x, y)
                z3 = (x,)
                z4 = (x, y)
                return z4""")

def test_tpl_Tuple_Intro_few():
    @fn
    def test():
        x [: string] = "test"
        z [: tpl[string, num]] = (x,)
        z
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_tpl_Tuple_Intro_many():
    @fn
    def test():
        x [: string] = "test"
        z [: tpl[string, string, num]] = (x, x)
        z
    with pytest.raises(tydy.TyError):
        test.typecheck()

class TestTplTupleIncIntro():
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x [: string] = "test"
            y [: num] = 0
            z1 [: tpl] = () 
            z2 [: tpl] = (x, y)
            z2
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), tpl[string, num]]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = 'test'
                y = 0
                z1 = ()
                z2 = (x, y)
                return z2""")

class TestTplDictIntroEmpty:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            z [: tpl[()]] = {}
            z
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), tpl[()]]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                z = (lambda x: ())(())
                return z""")

class TestTplDictIntro():
    @pytest.fixture
    def f(self):
        @fn
        def f():
            z1 [: tpl[string, num]] = {0 : "test", 1 : 0}
            z2 [: tpl['lbl0' : string, 'lbl1' : num]] = {lbl0: "test", lbl1: 0}
            z3 [: tpl['lbl0' : string, 'lbl1' : num]] = {lbl1: 0, lbl0: "test"}
            z3
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), tpl['lbl0' : string, 'lbl1' : num]]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                z1 = (lambda x: (x[0], x[1]))(('test', 0))
                z2 = (lambda x: (x[0], x[1]))(('test', 0))
                z3 = (lambda x: (x[1], x[0]))((0, 'test'))
                return z3""")

def test_tpl_Dict_Intro_few():
    @fn
    def test():
        z1 [: tpl[string, num]] = {0 : "test"}
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_tpl_Dict_Intro_many():
    @fn 
    def test():
        z1 [: tpl[string, num]] = {0 : "test", 1 : 0, 2 : 0}
    with pytest.raises(tydy.TyError):
        test.typecheck()

class TestTplDictIncIntro():
    @pytest.fixture
    def f(self):
        @fn
        def f():
            x [: string] = "test"
            y [: num] = 0
            z1 [: tpl] = {'lbl0' : x, 'lbl1' : y}
            z1
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), tpl['lbl0' : string, 'lbl1' : num]]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = 'test'
                y = 0
                z1 = (lambda x: (x[0], x[1]))((x, y))
                return z1""")

def test_tpl_Dict_empty_lbl():
    @fn
    def test():
        x [: string] = "test"
        z1 [: tpl] = {'' : x}
        z1
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_tpl_Dict_neg_lbl():
    @fn
    def test():
        x [: string] = "test"
        z1 [: tpl] = {-1 : x}
        z1
    with pytest.raises(tydy.TyError):
        test.typecheck()

def test_tpl_Dict_duplicate_lbl():
    @fn
    def test():
        x [: string] = "test"
        y [: num] = 0
        z1 [: tpl] = {lbl0: x, "lbl0": y}
        z1
    with pytest.raises(tydy.TyError):
        test.typecheck()

class TestTplXIntro:
    @pytest.fixture
    def f(self):
        @fn
        def f():
            X() [: tpl[()]]
            y1 = X() [: tpl]
            y1 [: tpl[()]]
            X(0, "test") [: tpl[num, string]]
            y2 = X(0 [: num], "test" [: string]) [: tpl]
            y2 [: tpl[num, string]]
            X(a=0, b="test") [: tpl['a' : num, 'b' : string]]
            y3 = X(a=0 [: num], b="test" [: string]) [: tpl]
            y3 [: tpl['a' : num, 'b' : string]]
            X(0, b="test") [: tpl[num, 'b' : string]]
            y4 = X(0 [: num], b="test" [: string]) [: tpl]
            y4 [: tpl[num, 'b' : string]]
            y4
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[(), tpl[num, 'b' : string]]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                (lambda x: ())(())
                y1 = (lambda x: ())(())
                y1
                (lambda x: (x[0], x[1]))((0, 'test'))
                y2 = (lambda x: (x[0], x[1]))((0, 'test'))
                y2
                (lambda x: (x[0], x[1]))((0, 'test'))
                y3 = (lambda x: (x[0], x[1]))((0, 'test'))
                y3
                (lambda x: (x[0], x[1]))((0, 'test'))
                y4 = (lambda x: (x[0], x[1]))((0, 'test'))
                y4
                return y4""")

class TestTplAttribute():
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {x : tpl['lbl0' : string]}
            x.lbl0
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[tpl['lbl0' : string], string]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return x[0]""")

class TestTplSubscript():
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {x : tpl[string, 'lbl1' : num]}
            (x[0], x['lbl1']) [: tpl]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[tpl[string, 'lbl1' : num], tpl[string, num]]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return (x[0], x[1])""")

#
# finsum
# 

def test_finsum_formation_no_variants():
    assert finsum[()].idx == odict()

def test_finsum_formation_one_variant_unit():
    assert finsum['A'].idx == odict((
        ('A', unit),
    ))

def test_finsum_formation_one_variant_num():
    assert finsum['A': num].idx == odict((
        ('A', num),
    ))

def test_finsum_formation_multi_variants():
    assert finsum['A': num, 'B', 'C': ieee].idx == odict((
        ('A', num),
        ('B', unit),
        ('C', ieee)
    ))

def test_finsum_equality():
    assert finsum['A': num, 'B', 'C': ieee] == finsum['A': num, 'B', 'C': ieee]
    assert finsum['A': num, 'B', 'C': ieee] == finsum['A': num, 'B': unit, 'C': ieee]

def test_finsum_variant_ordering():
    assert finsum['A': num, 'B'] != finsum['B', 'A': num]

def test_finsum_bad_variants():
    with pytest.raises(typy.TypeFormationError):
        finsum['']
    with pytest.raises(typy.TypeFormationError):
        finsum['': num]
    with pytest.raises(typy.TypeFormationError):
        finsum[0]
    with pytest.raises(typy.TypeFormationError):
        finsum[0: num]
    with pytest.raises(typy.TypeFormationError):
        finsum['x']
    with pytest.raises(typy.TypeFormationError):
        finsum['x': num]
    with pytest.raises(typy.TypeFormationError):
        finsum['A': num, 'A': num]
    with pytest.raises(typy.TypeFormationError):
        finsum['A': 0]
    with pytest.raises(typy.TypeFormationError):
        finsum[...]
    with pytest.raises(typy.TypeFormationError):
        finsum['A': int : int]
    with pytest.raises(typy.TypeFormationError):
        finsum['A': int, ...]
    
class TestFinSumIntro():
    @pytest.fixture
    def f(self):
        @fn
        def f():
            X [: finsum['X']]
            X [: finsum['X': unit]]
            X(3) [: finsum['X': num]]
        return f
    
    def test_type(self, f):
        assert f.typecheck() == fn[(), finsum['X': num]]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                'X'
                'X'
                return ('X', 3)""")

class TestFinSumMatch():
    @pytest.fixture
    def f(self):
        @fn
        def f(x, y):
            {x : finsum['X'], y : finsum['Y' : num]} >> num
            X = x
            match[x]
            with X: x
            let [Y(z)] = y
            match[y]
            with Y(3): 3
            with Y(z): z
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[finsum['X'], finsum['Y' : num], num]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x, y):
                __typy_let_scrutinee__ = x
                if (__typy_let_scrutinee__ == 'X'):
                    pass
                else:
                    raise __builtin__.Exception('Match failure.')
                __typy_match_scrutinee__ = x
                if (__typy_match_scrutinee__ == 'X'):
                    x
                else:
                    raise __builtin__.Exception('Match failure.')
                __typy_let_scrutinee__ = y
                if ((__typy_let_scrutinee__[0] == 'Y') and True):
                    z = __typy_let_scrutinee__[1]
                else:
                    raise __builtin__.Exception('Match failure.')
                __typy_match_scrutinee__ = y
                if ((__typy_match_scrutinee__[0] == 'Y') and (__typy_match_scrutinee__[1] == 3)):
                    return 3
                elif ((__typy_match_scrutinee__[0] == 'Y') and True):
                    __typy_id_z_1__ = __typy_match_scrutinee__[1]
                    return __typy_id_z_1__
                else:
                    raise __builtin__.Exception('Match failure.')""")

def test_finsum_bad_label():
    @fn
    def f():
        A [: finsum['B']]
    with pytest.raises(tydy.TyError):
        f.typecheck()

def test_finsum_bad_label_2():
    @fn
    def f(x):
        {x : num}
        A(x) [: finsum['B': num]]
    with pytest.raises(tydy.TyError):
        f.typecheck()

def test_finsum_missing_payload():
    @fn
    def f():
        A [: finsum['A': num]]
    with pytest.raises(tydy.TyError):
        f.typecheck()

def test_finsum_bad_args_1():
    @fn
    def f(x):
        {x : num}
        A(*x) [: finsum['A': num]]
    with pytest.raises(tydy.TyError):
        f.typecheck()

def test_finsum_bad_args_2():
    @fn
    def f(x):
        {x : num}
        A(**x) [: finsum['A': num]]
    with pytest.raises(tydy.TyError):
        f.typecheck()

def test_finsum_bad_args_3():
    @fn
    def f(x):
        {x : num}
        A(x=x) [: finsum['A': num]]
    with pytest.raises(tydy.TyError):
        f.typecheck()

def test_finsum_match_bad_label():
    @fn
    def f(x):
        {x : finsum['B']}
        match[x]
        with A: x
    with pytest.raises(tydy.TyError):
        f.typecheck()

def test_finsum_match_bad_label_2():
    @fn
    def f(x):
        {x : finsum['B': num]}
        match[x]
        with A(x): x
    with pytest.raises(tydy.TyError):
        f.typecheck()

def test_finsum_match_missing_payload():
    @fn
    def f(x):
        {x : finsum['A': num]}
        match[x]
        with A: x
    with pytest.raises(tydy.TyError):
        f.typecheck()

def test_finsum_match_bad_args_1():
    @fn
    def f(x):
        {x : finsum['A': num]}
        match[x]
        with A(*x): x
    with pytest.raises(tydy.TyError):
        f.typecheck()

def test_finsum_match_bad_args_2():
    @fn
    def f(x):
        {x : finsum['A': num]}
        match[x]
        with A(**x): x
    with pytest.raises(tydy.TyError):
        f.typecheck()

def test_finsum_match_bad_args_3():
    @fn
    def f(x):
        {x : finsum['A': num]}
        match[x]
        with A(x=x): x
    with pytest.raises(tydy.TyError):
        f.typecheck()

# 
# _equirec
# 

class TestEquirecNum:
    @pytest.fixture
    def ty(self):
        return typy._construct_equirec_ty(num_, lambda t: (), "num")

    def test_type_formation(self, ty):
        assert isinstance(ty, typy.Type)
    
    def test_type_refl(self, ty):
        assert ty == ty

    def test_type_refl_non_syntactic(self, ty):
        assert ty == typy._construct_equirec_ty(num_, lambda t: (), "num")

    def test_type_equirecursive(self, ty):
        assert ty == num

    def test_to_str(self, ty):
        assert str(ty) == "num"

    def test_anon_to_str(self, ty):
        assert ty.anon_to_str() == "num"

class TestEquirecRightNestedPair:
    @pytest.fixture
    def ty(self):
        return typy._construct_equirec_ty(tpl, lambda t: (num, t), "rnpair")

    def test_type_formation(self, ty):
        return isinstance(ty, typy.Type)

    def test_type_refl(self, ty):
        return ty == ty

    def test_type_refl_non_syntactic(self, ty):
        assert ty == typy._construct_equirec_ty(
            tpl, lambda t: (num, t), "rnpair2") # notice that the shortnames don't matter

    def test_type_equirecursive(self, ty):
        assert ty == tpl[num, ty] # the magic of imperative programming!

    def test_to_str(self, ty):
        assert str(ty) == "rnpair"

    def test_anon_to_str(self, ty):
        assert ty.anon_to_str() == "tpl[num, rnpair]"

def linkedlist(A):
    return typy._construct_equirec_ty(
        finsum,
        lambda t: (
            'Nil',
            slice('Cons', tpl[A, t])
        ),
        'linkedlist(' + str(A) + ')')

class TestEquirecNumList:
    @pytest.fixture
    def ty(self):
        return linkedlist(num)

    def test_type_formation(self, ty):
        return isinstance(ty, typy.Type)

    def test_type_refl(self, ty):
        return ty == ty

    def test_type_refl_non_syntactic(self, ty):
        assert ty == linkedlist(num)

    def test_type_equirecursive(self, ty):
        assert ty == finsum[
            'Nil',
            'Cons': tpl[num, ty]]

    def test_to_str(self, ty):
        assert str(ty) == "linkedlist(num)"

    def test_anon_to_str(self, ty):
        assert (
            (finsum[
                'Nil',
                'Cons': tpl[num, ty]])
            .anon_to_str()
            == "finsum['Nil', 'Cons': tpl[num, linkedlist(num)]]")

# 
# TyRecFnExpr
# 

from tydy.core._tyexps import TyRecFn, TyApExpr 

class TestTyRecFnExpr:
    @pytest.fixture
    def list(self):
        return TyRecFn(
            lambda list: lambda a: 
                finsum['Nil', 'Cons': tpl[a, list(a)]])
    
    @pytest.fixture
    def numlist(self, list):
        return list(num)

    @pytest.fixture
    def num_linkedlist(self):
        return linkedlist(num)

    @pytest.fixture
    def string_linkedlist(self):
        return linkedlist(string)

    def test_ty_expr(self, numlist):
        assert isinstance(numlist, TyApExpr)

    def test_ty_norm(self, numlist):
        norm = numlist.normalize()
        assert isinstance(norm, finsum)

    def test_refl(self, numlist):
        assert numlist == numlist
    
    def test_refl_non_syntactic(self, numlist):
        list2 = TyRecFn(
            lambda list: lambda a: 
                finsum['Nil', 'Cons': tpl[a, list(a)]])
        numlist2 = list2(num)
        assert numlist == numlist2
        assert numlist2 == numlist
        
    def test_not_refl_non_syntactic(self, numlist):
        list2 = TyRecFn(
            lambda list: lambda a: 
                finsum['Nil', 'Cons': tpl[a, list(a)]])
        numlist2 = list2(string)
        assert numlist != numlist2
        assert numlist2 != numlist

    def test_recty_eq(self, numlist):
        ll = linkedlist(num)
        assert numlist == ll
        assert ll == numlist

    def test_recty_neq(self, numlist):
        sll = linkedlist(string)
        assert numlist != sll
        assert sll != numlist
   
    def test_list_refl(self, list):
        assert list == list

    def test_list_refl_non_syntactic(self, list):
        list2 = TyRecFn(
            lambda list: lambda a:
                finsum['Nil', 'Cons': tpl[a, list(a)]])
        assert list == list2
        assert list2 == list

    def test_list_non_refl(self, list):
        non_list2 = TyRecFn(
            lambda list: lambda a:
                finsum['Nil', 'Cons': tpl[a, list(num)]])
        assert list != non_list2
        assert non_list2 != list

