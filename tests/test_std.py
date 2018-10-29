"""Standard library tests.

To run:
  $ py.test test_std.py
"""
import pytest
import ast

from typy.util.testing import ast_eq, trans_str, trans_truth

import typy
from typy._ty_exprs import CanonicalTy
from typy.std import boolean, unit, num, ieee, record, string, py, fn, variant, tpl
from typy._components import component # TODO

# 
# unit
# 

def test_unit_intro():
    @component
    def c():
        x [: typy.std.unit] = ()
        y = () [: typy.std.unit]

    # typechecking 
    assert c._members[0].ty == CanonicalTy(unit, ()) 
    assert c._members[1].ty == CanonicalTy(unit, ())

    # translation
    assert ast_eq(c._translation, """
        import builtins as __builtins__
        x = ()
        y = ()""")

    # evaluation
    assert c._module.x == ()
    assert c._module.y == ()

def test_unit_match():
    @component
    def c():
        x = () [: unit]
        [x].match
        with (): x

    assert ast_eq(c._translation, """
        import builtins as __builtins__
        x = ()
        __typy_scrutinee__ = x
        if True:
            x
        else:
            raise Exception('typy match failure')""")

def test_unit_intro_bad():
    with pytest.raises(typy.TyError):
        @component
        def c():
            x = ((), ()) [: unit]

def test_unit_match_bad():
    with pytest.raises(typy.TyError):
        @component
        def c():
            x = () [: unit]
            [x].match
            with (y, z): y

def test_unit_compare():
    @component
    def c():
        x = () [: unit]
        y = () [: unit]
        b1 = x == y
        b2 = x != y
        b3 = x is y
        b4 = x is not y

    # typechecking
    ty_unit = CanonicalTy(unit, ())
    ty_boolean = CanonicalTy(boolean, ())
    assert c._val_exports['x'].ty == ty_unit
    assert c._val_exports['y'].ty == ty_unit
    assert c._val_exports['b1'].ty == ty_boolean
    assert c._val_exports['b2'].ty == ty_boolean
    assert c._val_exports['b3'].ty == ty_boolean
    assert c._val_exports['b4'].ty == ty_boolean

# 
# boolean
# 

def test_boolean():
    @component
    def c():
        x [: boolean] = True
        y [: boolean] = False
        [x].match
        with True: y
        with False: y
        b1 = x == y
        b2 = x != y
        b3 = x is y
        b4 = x is not y
        b5 = x and y and x
        b6 = x or y or x
        if x:
            y
        else:
            y
        b7 = y if x else x
        b8 [: unit] = () if x else ()

    # typechecking
    assert c._val_exports['x'].ty == CanonicalTy(boolean, ())
    assert c._val_exports['y'].ty == CanonicalTy(boolean, ())
    assert c._val_exports['b1'].ty == CanonicalTy(boolean, ())
    assert c._val_exports['b2'].ty == CanonicalTy(boolean, ())
    assert c._val_exports['b3'].ty == CanonicalTy(boolean, ())
    assert c._val_exports['b4'].ty == CanonicalTy(boolean, ())
    assert c._val_exports['b5'].ty == CanonicalTy(boolean, ())
    assert c._val_exports['b6'].ty == CanonicalTy(boolean, ())
    assert c._val_exports['b7'].ty == CanonicalTy(boolean, ())
    assert c._val_exports['b8'].ty == CanonicalTy(unit, ())

    # translation
    assert ast_eq(c._translation, """
        import builtins as __builtins__
        x = True
        y = False
        __typy_scrutinee__ = x
        if __typy_scrutinee__:
            y
        elif (not __typy_scrutinee__):
            y
        else:
            raise Exception('typy match failure')
        b1 = (x == y)
        b2 = (x != y)
        b3 = (x is y)
        b4 = (x is not y)
        b5 = (x and y and x)
        b6 = (x or y or x)
        if x:
            y
        else:
            y
        b7 = (y if x else x)
        b8 = (() if x else ())""")

    # evaluation
    assert c._module.x == True
    assert c._module.y == False
    assert c._module.b1 == False
    assert c._module.b2 == True
    assert c._module.b3 == False
    assert c._module.b4 == True
    assert c._module.b5 == False
    assert c._module.b6 == True
    assert c._module.b7 == False
    assert c._module.b8 == ()

# 
# num
# 

def test_num():
    @component
    def c():
        x [: num] = 42
        y [: num] = -42
        [x].match
        with 42: y
        with -42: y
        with -z: z
        with +z: z
        b1 = x + y
        b2 = x - y
        b3 = x * y
        b4 = x / y
        b5 = x % y
        b6 = x ** y
        b7 = x << 2
        b8 = x >> 2
        b9 = x | 2
        b10 = x ^ 2
        b11 = x & 2
        b12 = x // 2
        b13 = ~x
        b14 = +x
        b15 = -x
        b16 = x == y
        b17 = x != y
        b18 = x < y <= y
        b19 = x > y >= y
        b20 = x is y
        b21 = x is not y
        # TODO methods?

    # typechecking
    num_ty = CanonicalTy(num, ())
    ieee_ty = CanonicalTy(ieee, ())
    boolean_ty = CanonicalTy(boolean, ())
    assert c._val_exports['x'].ty == num_ty
    assert c._val_exports['y'].ty == num_ty
    assert c._val_exports['b1'].ty == num_ty
    assert c._val_exports['b2'].ty == num_ty
    assert c._val_exports['b3'].ty == num_ty
    assert c._val_exports['b4'].ty == ieee_ty
    assert c._val_exports['b5'].ty == num_ty
    assert c._val_exports['b6'].ty == num_ty
    assert c._val_exports['b7'].ty == num_ty
    assert c._val_exports['b8'].ty == num_ty
    assert c._val_exports['b9'].ty == num_ty
    assert c._val_exports['b10'].ty == num_ty
    assert c._val_exports['b11'].ty == num_ty
    assert c._val_exports['b12'].ty == num_ty
    assert c._val_exports['b13'].ty == num_ty
    assert c._val_exports['b14'].ty == num_ty
    assert c._val_exports['b15'].ty == num_ty
    assert c._val_exports['b16'].ty == boolean_ty
    assert c._val_exports['b17'].ty == boolean_ty
    assert c._val_exports['b18'].ty == boolean_ty
    assert c._val_exports['b19'].ty == boolean_ty
    assert c._val_exports['b20'].ty == boolean_ty
    assert c._val_exports['b21'].ty == boolean_ty

    # translation
    assert ast_eq(c._translation, """
        import builtins as __builtins__
        x = 42
        y = (- 42)
        __typy_scrutinee__ = x
        if (__typy_scrutinee__ == 42):
            y
        elif ((__typy_scrutinee__ < 0) and ((- __typy_scrutinee__) == 42)):
            y
        elif ((__typy_scrutinee__ < 0) and True):
            _z_0 = (- __typy_scrutinee__)
            _z_0
        elif ((__typy_scrutinee__ > 0) and True):
            _z_1 = __typy_scrutinee__
            _z_1
        else:
            raise Exception('typy match failure')
        b1 = (x + y)
        b2 = (x - y)
        b3 = (x * y)
        b4 = (x / y)
        b5 = (x % y)
        b6 = (x ** y)
        b7 = (x << 2)
        b8 = (x >> 2)
        b9 = (x | 2)
        b10 = (x ^ 2)
        b11 = (x & 2)
        b12 = (x // 2)
        b13 = (~ x)
        b14 = (+ x)
        b15 = (- x)
        b16 = (x == y)
        b17 = (x != y)
        b18 = (x < y <= y)
        b19 = (x > y >= y)
        b20 = (x is y)
        b21 = (x is not y)""")

# 
# ieee
# 

def test_ieee():
    @component
    def c():
        x1 [: ieee] = 42
        x2 [: ieee] = 42.5
        y1 [: ieee] = -42
        y2 [: ieee] = -42.5
        nan [: ieee] = NaN
        inf [: ieee] = Inf
        ninf [: ieee] = -Inf
        n [: num] = 2
        [x1].match
        with 42: y1
        with 42.5: y1
        with -42: y2
        with -42.5: y2
        with NaN: inf
        with Inf: inf
        with -Inf: inf
        with -z: z
        with +z: z
        b1 = x1 + y1
        b1n = x1 + n
        b2 = x1 - y1
        b2n = n - y1
        b3 = x1 * y1
        b4 = x1 / y1
        b5 = x1 % y1
        b6 = x1 ** y1
        b12 = x1 // 2
        b14 = +x1
        b15 = -x1
        b16 = x1 == y1
        b17 = x1 != y1
        b18 = x1 < y1 <= y2
        b19 = x1 > y1 >= y2
        b20 = x1 is y1
        b21 = x1 is not y1
        # TODO: methods

    # typechecking
    num_ty = CanonicalTy(num, ())
    ieee_ty = CanonicalTy(ieee, ())
    boolean_ty = CanonicalTy(boolean, ())
    assert c._val_exports['x1'].ty == ieee_ty
    assert c._val_exports['x2'].ty == ieee_ty
    assert c._val_exports['y1'].ty == ieee_ty
    assert c._val_exports['y2'].ty == ieee_ty
    assert c._val_exports['nan'].ty == ieee_ty
    assert c._val_exports['inf'].ty == ieee_ty
    assert c._val_exports['ninf'].ty == ieee_ty
    assert c._val_exports['n'].ty == num_ty
    assert c._val_exports['b1'].ty == ieee_ty
    assert c._val_exports['b1n'].ty == ieee_ty
    assert c._val_exports['b2'].ty == ieee_ty
    assert c._val_exports['b2n'].ty == ieee_ty
    assert c._val_exports['b3'].ty == ieee_ty
    assert c._val_exports['b4'].ty == ieee_ty
    assert c._val_exports['b5'].ty == ieee_ty
    assert c._val_exports['b6'].ty == ieee_ty
    assert c._val_exports['b12'].ty == ieee_ty
    assert c._val_exports['b14'].ty == ieee_ty
    assert c._val_exports['b15'].ty == ieee_ty
    assert c._val_exports['b16'].ty == boolean_ty
    assert c._val_exports['b17'].ty == boolean_ty
    assert c._val_exports['b18'].ty == boolean_ty
    assert c._val_exports['b19'].ty == boolean_ty
    assert c._val_exports['b20'].ty == boolean_ty
    assert c._val_exports['b21'].ty == boolean_ty

    # translation
    assert trans_str(c._translation) == trans_truth("""
        import math as _typy_import_0
        import builtins as __builtins__
        x1 = 42
        x2 = 42.5
        y1 = (- 42)
        y2 = (- 42.5)
        nan = __builtins__.float('NaN')
        inf = __builtins__.float('Inf')
        ninf = (- __builtins__.float('Inf'))
        n = 2
        __typy_scrutinee__ = x1
        if (__typy_scrutinee__ == 42):
            y1
        elif (__typy_scrutinee__ == 42.5):
            y1
        elif ((__typy_scrutinee__ < 0.0) and ((- __typy_scrutinee__) == 42)):
            y2
        elif ((__typy_scrutinee__ < 0.0) and ((- __typy_scrutinee__) == 42.5)):
            y2
        elif _typy_import_0.isnan(__typy_scrutinee__):
            inf
        elif (__typy_scrutinee__ == __builtins__.float('Inf')):
            inf
        elif ((__typy_scrutinee__ < 0.0) and ((- __typy_scrutinee__) == __builtins__.float('Inf'))):
            inf
        elif ((__typy_scrutinee__ < 0.0) and True):
            _z_0 = (- __typy_scrutinee__)
            _z_0
        elif ((__typy_scrutinee__ > 0.0) and True):
            _z_1 = __typy_scrutinee__
            _z_1
        else:
            raise Exception('typy match failure')
        b1 = (x1 + y1)
        b1n = (x1 + n)
        b2 = (x1 - y1)
        b2n = (n - y1)
        b3 = (x1 * y1)
        b4 = (x1 / y1)
        b5 = (x1 % y1)
        b6 = (x1 ** y1)
        b12 = (x1 // 2)
        b14 = (+ x1)
        b15 = (- x1)
        b16 = (x1 == y1)
        b17 = (x1 != y1)
        b18 = (x1 < y1 <= y2)
        b19 = (x1 > y1 >= y2)
        b20 = (x1 is y1)
        b21 = (x1 is not y1)""")

# 
# string
# 

def test_string():
    @component
    def c():
        x1 [: string] = "test"
        jx1 [: string] = f"abc {x1} ghi"
        jx2 [: string] = f"{x1}"
        [x1].match
        with "": x1
        with "a" + y: y
        with y + "a": y
        with "t" + y + "t": y
        # with "t" + y + "t" + z: z  # TODO figure out appropriate conds for this
        with f"{x}": x
        with f"abc {x}": x
        with f"{x} def": x
        with f"abc {x} def": x
        # with f"abc {x} def {y} ghi": y # TODO figure out appropriate conds for this
        x2 = x1 + "a"
        x3 = "a" + x1
        x4 = x1[0]
        x5 = x1[0:3]
        x6 = x1[0:3:2]
        x7 = x1 == x2
        x8 = x1 != x2
        x9 = x1 < x2 <= x3
        x10 = x1 > x2 >= x3
        x11 = x1 is x2
        x12 = x1 is not x2
        # TODO * operator for repetition?
        # TODO in/not in?
        # TODO methods
        # TODO to_string logic for other primitives
        # TODO string formating?
        # TODO char patterns? separate type?
    
    string_ty = CanonicalTy(string, ())
    boolean_ty = CanonicalTy(boolean, ())
    v = c._val_exports
    assert v['x1'].ty == string_ty
    assert v['x2'].ty == string_ty
    assert v['x3'].ty == string_ty
    assert v['x4'].ty == string_ty
    assert v['x5'].ty == string_ty
    assert v['x6'].ty == string_ty
    assert v['x7'].ty == boolean_ty
    assert v['x8'].ty == boolean_ty
    assert v['x9'].ty == boolean_ty
    assert v['x10'].ty == boolean_ty
    assert v['x11'].ty == boolean_ty
    assert v['x12'].ty == boolean_ty

    # assert ast_eq(c._translation, "")

# 
# record
# 

def test_record():
    @component
    def c():
        t [type] = record[
            a : string,
            b : num]
        x [: t] = {
            a: "test",
            b: 2 }
        y [: t] = {
            b: 2,
            a: "test" }
        [x].match
        with {a: x, b: y}: x
        with {b: y, a: x}: x
        with {a, b}: a
        xa [: string] = x.a
        xb [: num] = x.b
        t2 [type] = record[
            b : num,
            a : string]
        y2 [: t2] = x

# 
# tpl
# 

def test_tpl():
    @component
    def c():
        t1 [type] = tpl[string]
        t2 [type] = tpl[a : string]
        t3 [type] = tpl[a : string, num]
        t4 [type] = tpl[string, b : num]
        t [type] = tpl[
            a : string,
            b : num]
        x1 [: t] = {
            a: "test",
            b: 2 }
        x2 [: t] = {
            b: 2,
            a: "test" }
        x3 [: t] = ("test", 2)
        [x1].match
        with {a: x, b: y}: x
        with {b: y, a: x}: x
        with {a, b}: a
        with {b, a}: a
        with (x, y): x
        # TODO + patterns
        xa [: string] = x1.a
        xb [: num] = x1.b
        t5 [type] = tpl[string, num]
        y1 [: t5] = ("test", 2)
        y_0 [: string] = y1[0]
        y_1 [: num] = y1[1]

# 
# variant
# 

def test_variant():
    @component
    def c():
        t0 [type] = variant[A]
        t1 [type] = variant[A(num)]
        t2 [type] = variant[A(num), B(string)]
        t3 [type] = variant[A(num, string), B(string, num)]
        x1 [: t3] = A(3, "test")
        x2 [: t3] = B("test", 3)
        [x2].match
        with A(x, y): x
        with B(x, y): y
        void [type] = variant[()]

# 
# fn
# 

def test_fn():
    @component
    def c():
        t0 [type] = fn[() > num]
        t1 [type] = fn[string > string]
        t2 [type] = fn[string, num > num]
        @t0
        def f1(): 3
        @t0
        def f1b() -> num: 3
        @t1
        def f2(x): x
        @t1
        def f2b(x : string) -> string: x
        @t2
        def f3(x, y): y
        @t2
        def f3b(x : string, y : num) -> num: y
        x1 [: t0] = lambda: 3 
        x2 [: t1] = lambda x: x
        x3 [: t2] = lambda x, y: y
        @fn
        def f11(x : string): x
        f11 [: t1]
        @fn
        def f12(x : string) -> string: ""
        f12 [: t1]
        f1()
        f2("string")
        f3("string", 0)
        @fn
        def f4(x : string):
            y [: string] = "ABC"
            y
        f4 [: fn[string > string]]
        @fn
        def f5(x : string) -> string:
            y [: string] = "ABC"
            "DEF"
        f5 [: fn[string > string]]
        @fn
        def f6(x : num) -> string:
            [x].match
            with 0: 
                "ABC"
            with x:
                "DEF"
        f6 [: fn[num > string]]
        @fn
        def f7(x : num):
            [x].match
            with 0:
                x
            with x:
                x
        f7 [: fn[num > num]]
        rfty [type] = fn[() > unit]
        @rfty
        def rf0():
            rf0()
        @fn
        def rf1() -> unit:
            rf1()
        rf1 [: fn[() > unit]]
        @fn
        def rf2(x : num) -> num:
            rf2(3)
        rf2 [: fn[num > num]]
        @fn
        def rf3(x : num) -> num:
            rf3(3)
        rf3 [: fn[num > num]]
        @fn
        def f8(x : num):
            @fn
            def fi1(y : num):
                x + y
            fi1
        @fn
        def f9(x : num):
            @fn
            def fi2(y : num):
                x + y
        @fn
        def f10(x : num) -> fn[num > num]:
            @fn
            def f(y):
                42
        @fn
        def f20(x : num):
            @fn
            def f(y : num):
                @fn
                def g(z : num):
                    x + y + z
        @fn
        def f21(x : num) -> fn[num > fn[num > num]]:
            def f(y):
                def g(z):
                    x + y + z

        ty22 [type] = fn[num > num]
        @fn
        def f22(x : num) -> fn[num > num]:
            @ty22
            def f(y):
                x

        ty23 [type] = fn[num > num]
        @fn
        def f23(x : num) -> fn[num > num]:
            @fn
            def f(y):
                x

    # assert ast_eq(c._translation, "")
    
# 
# py
# 

def test_py():
    set2 = set
    class C(object): pass
    D = 5
    @component
    def c():
        # literals
        int_intro [: py] = 4
        int_intro2 [: py] = -4
        float_intro [: py] = 3.14
        float_intro2 [: py] = -3.14
        string_intro [: py] = "abc"
        string_intro2 [: py] = f'abc {string_intro} def'
        string_intro3 [: py] = f'abc {string_intro!s} def'
        string_intro4 [: py] = f'abc {string_intro!s:3} def'
        string_intro5 [: py] = f'abc {string_intro!s:{int_intro}.{int_intro}} def' # TODO this is a bug in the pretty-printer
        string_intro6 [: py] = f'{string_intro}'
        true_intro [: py] = True
        false_intro [: py] = False
        none_intro [: py] = None
        not_implemented_intro [: py] = NotImplemented
        ellipsis_intro [: py] = Ellipsis
        dict_intro [: py] = { None : "abc", 3.14 : None }
        set_intro [: py] = { "abc", 3.14, None }
        empty_set_intro = set()
        empty_set_intro2 = set2()
        list_intro [: py] = [ "abc", { }, 1.23 ]
        unit_intro [: py] = ()
        tuple_intro [: py] = ( "abc", 3.14 )
        bytes_intro [: py] = b'test'
        cls_intro [: py] = C()
        name_ok_ana [: py] = D
        name_ok_syn = D
        E = D
        f = E
        
        # function definitions
        @py
        def f1():
            3
        f1()

        @py
        def f2(x, y):
            x + y
        f2(3, 4)
        f2(3, y=4)
        f2(x=3, y=4)

        @py
        def f3(x, *y):
            y
        f3(True, False, None)
        f3(True)
        f3(True, *(False, None))
        
        @py
        def f4(x, *y, **z):
            z
        f4(True)
        f4(3, 4, 5, 6)
        f4(3, 4, 5, 6, y=4)
        f4(3, 4, 5, 6, **{'y': 4, 'z': 6})

        @py
        def f5(x, y=None):
            x
        f5(None)
        f5(None, 4)
        f5(None, y=5)

        @py
        def f6(x : None, y : None = 3):
            y
        f6(None)
        f6(None, 4)
        f6(None, y=6)

        @py
        def f7(x : None, y : None = 3, *z : None, **q : None):
            q
        f7(3)
        
        @py
        def f8():
            @py
            def f(x):
                x
            @f
            def g(x):
                x
        f8()

        @py
        def f9():
            x = 3
            x
        f9()

        # lambdas
        lam1 [: py] = lambda: 3
        lam2 [: py] = lambda x: 3
        lam3 [: py] = lambda x, y: x + y
        lam4 [: py] = lambda x, y=None, *z, **q: x + y

        # comprehensions
        dict_comprehension [: py] = {x: y 
                                     for x in list_intro if x == true_intro 
                                     for y in set_intro if y == false_intro}
        set_comprehension [: py] = {x 
                                    for x in list_intro if x == true_intro 
                                    for y in set_intro if y == false_intro}
        list_comprehension [: py] = [x
                                     for x in list_intro if x == true_intro
                                     for y in set_intro if y == false_intro]
        generator_test [: py] = (x
                                 for x in list_intro if x == true_intro
                                 for y in set_intro if y == false_intro)

        # if statements
        if true_intro:
            int_intro
        elif false_intro:
            int_intro
        else:
            int_intro

        # expression-level operations
        x [: py] = 0
        y [: py] = 1
        z [: py] = "abc"
        # bool ops
        bool_op1 = x and y and z
        bool_op2 = x or y or z
        bool_op3 [: py] = True and False and True
        bool_op4 [: py] = True or False or True
        # bin ops
        add = x + y
        sub = x - y
        mult = x * y
        div = x / y
        mod = x % y
        pow = x ** y
        lshift = x << y
        rshift = x >> y
        bitor = x | y
        bitxor = x ^ y
        bitand = x & y
        floordiv = x // y
        matmult = x @ y if False [: boolean] else 0 # to avoid run-time exception
        # unary ops
        invert = ~x
        op_not = not x
        uadd = +x
        usub = -x
        # comparison ops
        compares = x == y != z < x <= y > z >= x is y is not z in x not in y
        # if expressions
        ifexp = (1 [: num]) if x else (2 [: num])
        ifexp [: num]
        ifexp2 [: py] = 123 if x else 456
        # call
        call = x(y, z, *z, a=x, b=y, **x) if False [: boolean] else 0
        # attribute access
        attr = x.bit_length()
        # attribute assignment
        if false_intro:
            x.attr = 55
            x.attr += 55
        elif false_intro:
            x.attr *= 55
            x.attr = 44
        # subscripting
        subscript1 = x[y] if False [: boolean] else x
        subscript3 = x[x:y:z] if False [: boolean] else 0
        subscript4 = x[y, z] if False [: boolean] else 0
        subscript5 = x[y, y:z, x:y:z] if False [: boolean] else 0
        subscript6 = x[...] if False [: boolean] else 0
        subscript7 = list_intro[:]
        ss_00 = list_intro[:]
        ss_01 = list_intro[:_]
        # ss_02 = list_intro[:1] # NOPE, this one is a type asc.
        ss_10 = list_intro[_:]
        ss_11 = list_intro[_:_]
        ss_12 = list_intro[_:1]
        ss_20 = list_intro[1:]
        ss_21 = list_intro[1:_]
        ss_22 = list_intro[1:1]
        ss_000 = list_intro[::]
        ss_001 = list_intro[::_]
        ss_002 = list_intro[::1]
        ss_010 = list_intro[:_:]
        ss_011 = list_intro[:_:_]
        ss_012 = list_intro[:_:1]
        # ss_020 = list_intro[:1:] # NOPE, parsed identically to list_intro[:1] unfortunately
        ss_021 = list_intro[:1:_]
        ss_022 = list_intro[:1:1]
        ss_100 = list_intro[_::]
        ss_101 = list_intro[_::_]
        ss_102 = list_intro[_::1]
        ss_110 = list_intro[_:_:]
        ss_111 = list_intro[_:_:_]
        ss_112 = list_intro[_:_:1]
        ss_120 = list_intro[_:1:]
        ss_121 = list_intro[_:1:_]
        ss_122 = list_intro[_:1:1]
        ss_200 = list_intro[1::]
        ss_201 = list_intro[1::_]
        ss_202 = list_intro[1::1]
        ss_210 = list_intro[1:_:]
        ss_211 = list_intro[1:_:_]
        ss_212 = list_intro[1:_:1]
        ss_220 = list_intro[1:1:]
        ss_221 = list_intro[1:1:_]
        ss_222 = list_intro[1:1:1]

        # subscript assignment
        if false_intro:
            x[432] = 423
            x[1:2] = 432
            x[_:2] = 432
            x[_:2] /= 432
            x[432] += 542
        elif false_intro:
            x[532] *= 312
            x["a"] = "bcd"

        # pattern matching
        [x].match 
        with str(s): 
            s [: string]
            x
        with str("ABC"):
            x
        with str(y + "ABC"):
            y [: string]
            x
        with "ABC": # same as str("ABC")
            x
        with y + "ABC": # same as str(y + "ABC")
            y [: string]
            x
        with "ABC" + y: # same as str("ABC" + y)
            y [: string]
            x
        with f"{y}":
            y [: string]
            x
        with f"{y} abc":
            y [: string]
            x
        with f"abc {y}":
            y [: string]
            x
        with f"abc {y} def":
            y [: string]
            x
        with b'test':
            x
        with int(n): 
            n [: num]
            x
        with 0: # same as int(0)
            x
        with -4: # same as int(-4)
            x
        with float(n):
            n [: ieee]
            x
        with bool(b): 
            b [: boolean]
            x
        with True: # same as bool(True)
            x
        with False: # same as bool(False)
            x
        with None:
            x
        with not None:
            x
        with NotImplemented:
            x
        with Ellipsis:
            x
        with (x, y, z):  
            x [: py]
            y [: py]
            z [: py]
        with (x, y, z) + e:
            x [: py]
            y [: py]
            z [: py]
            e [: py]
        with e + (x, y, z):
            x [: py]
            y [: py]
            z [: py]
            e [: py]
        with (x, y, z)(a):
            x [: py]
            y [: py]
            z [: py]
            a [: tpl[py, py, py]]
            a[0]
        with (x, y, z)(a) + e:
            x [: py]
            y [: py]
            z [: py]
            a [: tpl[py, py, py]]
            e [: py]
            a[0]
        with e + (x, y, z)(a):
            x [: py]
            y [: py]
            z [: py]
            a [: tpl[py, py, py]]
            e [: py]
            a[0]
        with [x, y, z]:
            x [: py]
            y [: py]
            z [: py]
        with {'x': x, 'y': y, 'z': z}:
            x [: py]
            y [: py]
            z [: py]
        with x(attr1=pat1, attr2=pat2):
            pat1 [: py]
            pat2 [: py]

        # TODO class definitions
        # TODO top-level stuff
        # TODO conversions from other types
        # TODO for, break, continue
        # TODO while, break, continue
        # TODO if
        # TODO assert
        # TODO global + assignment logic
        # TODO pass
        # TODO with???
        # TODO exceptions

    assert ast_eq(c._translation, "")

# 
# module system
# 

def test_module_value_access():
    @component
    def m1():
        x [: py] = 34

    @component
    def m2():
        y = m1.x

