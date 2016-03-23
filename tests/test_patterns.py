"""Tests of pattern matching."""
import pytest

import typy
from tydy import *
from tydy.util.testing import *

# pattern matching basics
class TestVariablePatternAna:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {unit} >> unit
            {x} is {y: y}
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[unit, unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return """
                    "(lambda __typy_scrutinee__: "
                       "((lambda y: y)(__typy_scrutinee__) if True "
                       "else (_ for _ in ()).throw(__builtin__.Exception('Match failure.')))"
                    ")(x)""") 

class TestVariablePatternAnaPropagates:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {boolean} >> boolean
            {x} is {y: True}
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[boolean, boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return (lambda __typy_scrutinee__: """
                    "((lambda y: True)(__typy_scrutinee__) if True "
                    "else (_ for _ in ()).throw(__builtin__.Exception('Match failure.')))"
                ")(x)") 

class TestVariablePatternMatchAna:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {unit} >> unit
            match[x]
            with y:
                y
            with _: # redundant
                ()
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[unit, unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                __typy_match_scrutinee__ = x
                if True:
                    y = __typy_match_scrutinee__
                    return y
                elif True:
                    return ()
                else:
                    raise __builtin__.Exception('Match failure.')""")

class TestVariablePatternMatchAsc:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {unit}
            match[x] [: boolean]
            with y:
                True
            with _:
                False
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[unit, boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                __typy_match_scrutinee__ = x
                if True:
                    y = __typy_match_scrutinee__
                    return True
                elif True:
                    return False
                else:
                    raise __builtin__.Exception('Match failure.')""")

class TestVariablePatternSyn:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {boolean}
            {x} is {y: y}
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[boolean, boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return (lambda __typy_scrutinee__: """
                    "((lambda y: y)(__typy_scrutinee__) if True "
                    "else (_ for _ in ()).throw(__builtin__.Exception('Match failure.')))"
                ")(x)")

class TestVariablePatternMatchSyn:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {boolean}
            match[x]
            with True:
                not x
            with _:
                False
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[boolean, boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                __typy_match_scrutinee__ = x
                if __typy_match_scrutinee__:
                    return (not x)
                elif True:
                    return False
                else:
                    raise __builtin__.Exception('Match failure.')""")

def test_underscore_pattern():
    @fn
    def test(x):
        {boolean}
        {x} is {_: _}

    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_underscore_pattern_match():
    @fn
    def test(x):
        {boolean}
        match[x]
        with _:
            _

    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_invalid_pattern_form():
    @fn
    def test(x):
        {boolean}
        {x} is {3 + 3: x}

    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestMultipleRulesAna:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {boolean} >> boolean
            {x} is {y: True, y: y}
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[boolean, boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return (lambda __typy_scrutinee__: """
                  "((lambda y: True)(__typy_scrutinee__) if True "
                  "else ("
                    "(lambda __typy_id_y_1__: __typy_id_y_1__)(__typy_scrutinee__) if True "
                    "else (_ for _ in ()).throw(__builtin__.Exception('Match failure.'))))"
                ")(x)") 

def test_pop():
    @fn
    def test(x):
        {boolean}
        {x} is {y: True, z: y}
    
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_match_pop():
    @fn
    def test(x):
        {boolean}
        match[x]
        with y:
            True
        with z:
            y

    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_invalid_form():
    @fn
    def test(x):
        {num}
        {x} is {y: y} + 5
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestOperations:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {num}
            ({x} is {y: y}) + 5
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[num, num]
    
    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return ((lambda __typy_scrutinee__: """
                    "((lambda y: y)(__typy_scrutinee__) if True "
                    "else (_ for _ in ()).throw(__builtin__.Exception('Match failure.')))"
                ")(x) + 5)""")

class TestMatchOperations:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {num}
            with let[z]:
                match[x]
                with y:
                    y
            z + 5
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[num, num]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                __typy_match_scrutinee__ = x
                if True:
                    y = __typy_match_scrutinee__
                    __typy_with_scrutinee__ = y
                else:
                    raise __builtin__.Exception('Match failure.')
                z = __typy_with_scrutinee__
                return (z + 5)""")

class TestDoMatch:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {num}
            match[x]
            with y:
                pass
            x
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[num, num]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                __typy_match_scrutinee__ = x
                if True:
                    y = __typy_match_scrutinee__
                    pass
                else:
                    raise __builtin__.Exception('Match failure.')
                return x""")

class TestBooleanPattern:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {boolean}
            {{x} is {True: x, False: x}} is {
                False: x,
                _: x
            }
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[boolean, boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return (lambda __typy_scrutinee__: """
                    "(x if (not __typy_scrutinee__) "
                    "else ("
                    "x if True "
                    "else (_ for _ in ()).throw("
                    "__builtin__.Exception('Match failure.'))))"
                ")((lambda __typy_scrutinee__: "
                    "(x if __typy_scrutinee__ "
                    "else ("
                    "x if (not __typy_scrutinee__) "
                    "else (_ for _ in ()).throw("
                    "__builtin__.Exception('Match failure.')))))(x))""")

class TestBooleanPatternMatch:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {boolean}
            with let[_x]:
                match[x]
                with True:
                    x
                with False:
                    x
            match[_x]
            with False:
                x
            with _:
                x
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[boolean, boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                __typy_match_scrutinee__ = x
                if __typy_match_scrutinee__:
                    __typy_with_scrutinee__ = x
                elif (not __typy_match_scrutinee__):
                    __typy_with_scrutinee__ = x
                else:
                    raise __builtin__.Exception('Match failure.')
                _x = __typy_with_scrutinee__
                __typy_match_scrutinee__ = _x
                if (not __typy_match_scrutinee__):
                    return x
                elif True:
                    return x
                else:
                    raise __builtin__.Exception('Match failure.')""")

class TestBooleanDestructuringAssign:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {boolean}
            True = x # noqa
            x
        return f

    def test_type(self, f):
        f.typecheck() == fn[boolean, boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                __typy_let_scrutinee__ = x
                if __typy_let_scrutinee__:
                    pass
                else:
                    raise __builtin__.Exception('Match failure.')
                return x""")

class TestBooleanLet:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {boolean}
            let [True] = x
            x
        return f

    def test_type(self, f):
        f.typecheck() == fn[boolean, boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                __typy_let_scrutinee__ = x
                if __typy_let_scrutinee__:
                    pass
                else:
                    raise __builtin__.Exception('Match failure.')
                return x""")

class TestNumPattern:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {num}
            {x} is {0: x, 5: x + x}
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[num, num]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return (lambda __typy_scrutinee__: """
                    "(x if (__typy_scrutinee__ == 0) "
                    "else ((x + x) if (__typy_scrutinee__ == 5) "
                    "else (_ for _ in ()).throw(__builtin__.Exception('Match failure.'))))"
                ")(x)")

class TestNumLet:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {num}
            let [5] = x
            x
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[num, num]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                __typy_let_scrutinee__ = x
                if (__typy_let_scrutinee__ == 5):
                    pass
                else:
                    raise __builtin__.Exception('Match failure.')
                return x""")

class TestIEEEPattern:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {ieee}
            {x} is {0: x, 5.5: x + x}
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[ieee, ieee]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return (lambda __typy_scrutinee__: """
                    "(x if (__typy_scrutinee__ == 0.0) "
                    "else ((x + x) if (__typy_scrutinee__ == 5.5) "
                    "else (_ for _ in ()).throw("
                       "__builtin__.Exception('Match failure.')))))(x)")

class TestIEEENamePattern:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {ieee}
            {x} is {
                NaN: x,
                Inf: x,
                -Inf: x,
                +Inf: x}
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[ieee, ieee]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return (lambda __typy_scrutinee__: """
                    "(x if __builtin__.__import__('math').isnan(__typy_scrutinee__) "
                    "else (x if (__typy_scrutinee__ == __builtin__.float('Inf')) "
                    "else (x if (__typy_scrutinee__ == __builtin__.float('-Inf')) "
                    "else (x if (__typy_scrutinee__ == __builtin__.float('Inf')) "
                    "else (_ for _ in ()).throw("
                    "__builtin__.Exception('Match failure.'))))))"
                ")(x)")

class TestCplxNumPattern:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {cplx}
            {x} is {0: x, 5.5: x + x, 6j: x + x + x}
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[cplx, cplx]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return (lambda __typy_scrutinee__: """
                    "(x if (__typy_scrutinee__ == 0j) "
                    "else ((x + x) if (__typy_scrutinee__ == (5.5+0j)) "
                    "else (((x + x) + x) if (__typy_scrutinee__ == 6j) "
                    "else (_ for _ in ()).throw("
                       "__builtin__.Exception('Match failure.'))))))(x)")

class TestCplxTuplePattern:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {cplx} >> ieee
            {x} is {
                (0, 1.0): 0, 
                (y, 2.0): y,
                (3.0, y): y,
                (y, z): y + z
            }
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[cplx, ieee]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return (lambda __typy_scrutinee__: """
                    "(0.0 if ((__typy_scrutinee__.real == 0.0) "
                       "and (__typy_scrutinee__.imag == 1.0)) "
                    "else ((lambda y: y)(__typy_scrutinee__.real) "
                       "if (True and (__typy_scrutinee__.imag == 2.0)) "
                    "else ((lambda __typy_id_y_1__: __typy_id_y_1__)("
                       "__typy_scrutinee__.imag) if "
                       "((__typy_scrutinee__.real == 3.0) and True) "
                    "else ((lambda __typy_id_y_2__, z: (__typy_id_y_2__ + z))("
                       "__typy_scrutinee__.real, "
                       "__typy_scrutinee__.imag) if (True and True) "
                    "else (_ for _ in ()).throw("
                       "__builtin__.Exception('Match failure.')))))))(x)")

class TestCplxTuplePatternMatch:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {cplx} >> ieee
            match[x]
            with (0, 1.0): 0 
            with (y, 2.0): y 
            with (3.0, y): y 
            with (y, z): y + z 
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[cplx, ieee]

    def test_translation(self, f):
        translation_eq(f, """
        def f(x):
            __typy_match_scrutinee__ = x
            if ((__typy_match_scrutinee__.real == 0.0) and (__typy_match_scrutinee__.imag == 1.0)):
                return 0.0
            elif (True and (__typy_match_scrutinee__.imag == 2.0)):
                y = __typy_match_scrutinee__.real
                return y
            elif ((__typy_match_scrutinee__.real == 3.0) and True):
                __typy_id_y_1__ = __typy_match_scrutinee__.imag
                return __typy_id_y_1__
            elif (True and True):
                __typy_id_y_2__ = __typy_match_scrutinee__.real
                z = __typy_match_scrutinee__.imag
                return (__typy_id_y_2__ + z)
            else:
                raise __builtin__.Exception('Match failure.')""")

class TestCplxTupleLet:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {cplx} >> ieee
            (y, z) = x
            let [(y, z)] = x
            let [(y, z) : cplx] = (y, z)
            y + z
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[cplx, ieee]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                __typy_let_scrutinee__ = x
                if (True and True):
                    y = __typy_let_scrutinee__.real
                    z = __typy_let_scrutinee__.imag
                else:
                    raise __builtin__.Exception('Match failure.')
                __typy_let_scrutinee__ = x
                if (True and True):
                    __typy_id_y_1__ = __typy_let_scrutinee__.real
                    __typy_id_z_1__ = __typy_let_scrutinee__.imag
                else:
                    raise __builtin__.Exception('Match failure.')
                __typy_let_scrutinee__ = __builtin__.complex(__typy_id_y_1__, __typy_id_z_1__)
                if (True and True):
                    __typy_id_y_2__ = __typy_let_scrutinee__.real
                    __typy_id_z_2__ = __typy_let_scrutinee__.imag
                else:
                    raise __builtin__.Exception('Match failure.')
                return (__typy_id_y_2__ + __typy_id_z_2__)""")

def test_cplx_tuple_duplicate_vars():
    @fn
    def test(x):
        {cplx} >> ieee
        {x} is {
            (y, y): y + y
        }
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_cplx_tuple_nested():
    @fn
    def test(x):
        {cplx} >> ieee
        {x} is {
            ((y, z), q): y + y
        }
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestStringPattern:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {string}
            {x} is {
                "": x,
                "ABC": x,
                "DEF": x
            }
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[string, string]
    
    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return (lambda __typy_scrutinee__: """
                    "(x if (__typy_scrutinee__ == '') "
                    "else (x if (__typy_scrutinee__ == 'ABC') "
                    "else (x if (__typy_scrutinee__ == 'DEF') "
                    "else (_ for _ in ()).throw("
                       "__builtin__.Exception('Match failure.')))))"
                ")(x)")

class TestStringLet:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {string}
            let ["test"] = x
            x
        return f
    
    def test_type(self, f):
        assert f.typecheck() == fn[string, string]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                __typy_let_scrutinee__ = x
                if (__typy_let_scrutinee__ == 'test'):
                    pass
                else:
                    raise __builtin__.Exception('Match failure.')
                return x""")

class TestTplTuplePattern:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {tpl[num, ieee]} >> tpl[ieee, num]
            {x} is {
                (y, z): (z, y)
            }
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[tpl[num, ieee], tpl[ieee, num]]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return (lambda __typy_scrutinee__: """
                    "((lambda y, z: (z, y))(__typy_scrutinee__[0], __typy_scrutinee__[1]) "
                    "if (True and True) "
                    "else (_ for _ in ()).throw("
                    "__builtin__.Exception('Match failure.')))"
                ")(x)""")

class TestTplNestedTuplePattern:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {tpl[tpl[num, num], tpl[ieee, ieee]]} >> tpl[tpl[ieee, num], tpl[ieee, num]]
            {x} is {
                ((a, b), (c, d)): ((c, a), (d, b))
            }
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[
            tpl[tpl[num, num], tpl[ieee, ieee]], 
            tpl[tpl[ieee, num], tpl[ieee, num]]]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return (lambda __typy_scrutinee__: """
                    "((lambda a, b, c, d: ((c, a), (d, b)))("
                    "__typy_scrutinee__[0][0], "
                    "__typy_scrutinee__[0][1], "
                    "__typy_scrutinee__[1][0], "
                    "__typy_scrutinee__[1][1]) "
                    "if ((True and True) and (True and True)) "
                    "else (_ for _ in ()).throw("
                    "__builtin__.Exception('Match failure.')))"
                ")(x)""")

class TestTplLet:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {tpl[tpl[num, num], tpl[ieee, ieee]]}
            ((a, b), (c, d)) = x
            ((c, a), (d, b)) [: tpl]
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[
            tpl[tpl[num, num], tpl[ieee, ieee]],
            tpl[tpl[ieee, num], tpl[ieee, num]]]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                __typy_let_scrutinee__ = x
                if ((True and True) and (True and True)):
                    a = __typy_let_scrutinee__[0][0]
                    b = __typy_let_scrutinee__[0][1]
                    c = __typy_let_scrutinee__[1][0]
                    d = __typy_let_scrutinee__[1][1]
                else:
                    raise __builtin__.Exception('Match failure.')
                return ((c, a), (d, b))""")

def test_Tpl_too_few():
    @fn
    def test(x):
        {tpl[num, num, num]} >> num
        {x} is {
            (y, z): y
        }
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Tpl_too_many():
    @fn
    def test(x):
        {tpl[num, num]} >> num
        {x} is {
            (a, b, c): a
        }
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Tpl_duplicate():
    @fn
    def test(x):
        {tpl[num, num]} >> num
        {x} is {
            (y, y): y
        }
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestTplDictPattern:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {tpl['a' : num, 3 : ieee]} >> tpl[num, ieee]
            {x} is {
                {'a': 5, 3: _}: (0, 0),
                {3: y, 'a': x}: (x, y)
            }
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[
            tpl['a' : num, 3 : ieee],
            tpl[num, ieee]]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return (lambda __typy_scrutinee__: ((0, 0.0) if ((__typy_scrutinee__[0] == 5) and True) else ((lambda y, __typy_id_x_1__: (__typy_id_x_1__, y))(__typy_scrutinee__[1], __typy_scrutinee__[0]) if (True and True) else (_ for _ in ()).throw(__builtin__.Exception('Match failure.')))))(x)""") # noqa

def test_Tpl_Dict_too_few():
    @fn
    def test(x):
        {tpl['a' : num, 'b' : ieee]} >> num
        {x} is {
            {'a': x}: x
        }
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Tpl_Dict_too_many():
    @fn
    def test(x):
        {tpl['a' : num, 'b' : ieee]} >> num
        {x} is {
            {'a': x, 'b': y, 'c': z}: x
        }
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Tpl_Dict_duplicate_label():
    @fn
    def test(x):
        {tpl['a' : num, 'b' : ieee]} >> num
        {x} is {
            {'a': x, 'a': y}: x
        }
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Tpl_Dict_invalid():
    @fn
    def test(x):
        {tpl['a' : num]} >> num
        {x} is {
            {'c': x}: x
        }
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Tpl_Dict_duplicate_var():
    @fn
    def test(x):
        {tpl['a' : num, 'b' : ieee]} >> num
        {x} is {
            {'a': x, 'b': x}: x
        }
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestTplXPattern:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {tpl[num, ieee, 'a' : num, 'b' : ieee]} >> tpl[num, ieee, num, ieee]
            {x} is {
                X(a, b, a=x, b=y): (a, b, x, y)
            }
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[
            tpl[num, ieee, 'a': num, 'b': ieee],
            tpl[num, ieee, num, ieee]]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return (lambda __typy_scrutinee__: ((lambda a, b, __typy_id_x_1__, y: (a, b, __typy_id_x_1__, y))(__typy_scrutinee__[0], __typy_scrutinee__[1], __typy_scrutinee__[2], __typy_scrutinee__[3]) if (True and True and True and True) else (_ for _ in ()).throw(__builtin__.Exception('Match failure.'))))(x)""") # noqa

def test_Tpl_X_invalid_label():
    @fn
    def test(x):
        {tpl['a' : num]} >> num
        {x} is {
            X(x): x
        }
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Tpl_X_invalid_label_2():
    @fn
    def test(x):
        {tpl['a' : num]} >> num
        {x} is {
            X(b=x): x
        }
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Tpl_X_duplicate_var():
    @fn
    def test(x):
        {tpl[num, 'a' : num]} >> num
        {x} is {
            X(y, a=y): y
        }
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Tpl_X_duplicate_var_2():
    @fn
    def test(x):
        {tpl[num, 'a' : num, 'b' : num]} >> num
        {x} is {
            X(y, a=z, b=z): z
        }
    with pytest.raises(typy.TypeError):
        test.typecheck()

