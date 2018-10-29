"""Testing the examples from the GPCE 2016 paper.

To run:
  $ py.test test_gpce16.py
"""
import pytest
import ast

import typy
from typy.std import component, unit, record, string, py, fn, finsum, tpl

class TestGPCEExamples:
    @pytest.fixture
    def Listing1(self):
        # simplified to use string rather than string_in for now
        # TODO string_in
        @component
        def Listing1():
            Account [type] = record[
                name        : string,
                account_num : string,
                memo        : py
            ]

            test_acct [: Account] = {
                name: "Harry Q. Bovik",
                account_num: "00-12345678",
                memo: { }
            }

        return Listing1

    def test_Listing1(self, Listing1):
        c = Listing1
        assert isinstance(c, typy.Component)

        # parsing
        assert isinstance(c._members, tuple)
        assert len(c._members) == 2
        
        assert isinstance(c._members[0], typy._components.TypeMember)
        assert c._members[0].id == "Account"
        assert isinstance(c._members[0].uty_expr, typy._ty_exprs.UCanonicalTy)
        assert isinstance(c._members[0].uty_expr.fragment_ast, ast.Name)
        assert isinstance(c._members[0].uty_expr.idx_ast, ast.ExtSlice)

        assert isinstance(c._members[1], typy._components.ValueMember)
        assert c._members[1].id == "test_acct"
        assert isinstance(c._members[1].uty, typy._ty_exprs.UName)
        assert c._members[1].uty.id == "Account"

        # checking
        assert isinstance(c._members[1].ty, typy._ty_exprs.CanonicalTy)
        assert c._members[1].ty.fragment == record
        assert isinstance(c._members[0].ty.idx, dict)
        assert c._members[1].ty.idx["name"].fragment == string
        assert c._members[1].ty.idx["account_num"].fragment == string
        assert c._members[1].ty.idx["memo"].fragment == py
        
        assert isinstance(c._members[1].ty, typy._ty_exprs.CanonicalTy)
        assert c._members[1].ty.fragment == record

        # translation and evaluation
        assert c._module.test_acct == ("00-12345678", 
                                       { }, "Harry Q. Bovik")

    @pytest.fixture
    def Listing4(self, Listing1):
        @component
        def Listing4():
            @fn
            def hello(account : Listing1.Account):
                """Computes a string greeting."""
                name = account.name 
                "Hello, " + name
            
            hello_test = hello(Listing1.test_acct)
            # TODO print
        
        return Listing4

    def test_Listing4(self, Listing4):
        c = Listing4
        assert isinstance(c, typy.Component)
        
        assert c._module.hello(("00-12345678", 
                               { }, "Harry Q. Bovik")) == "Hello, Harry Q. Bovik"
        assert c._module.hello_test == "Hello, Harry Q. Bovik"

    @pytest.fixture
    def Listing7(self):
        @component
        def Listing7():
            tree(+a) [type] = finsum[
                Empty,
                Node(tree(+a), tree(+a)),
                Leaf(+a)
            ]

            @fn
            def map(f : fn[+a, +b], 
                    t : tree(+a)) -> tree(+b):
                [t].match
                with Empty: Empty
                with Node(left, right):
                    Node(map(f, left), map(f, right))
                with Leaf(x): Leaf(f(x))

        return Listing7
        # TODO type functions
        # TODO finsum init_idx
        # TODO recursive types
        # TODO polymorphic functions
        # TODO pattern matching
        # TODO name literals
        # TODO recursive functions

    @pytest.fixture
    def Listing9(self, Listing1):
        @component
        def Listing9():
            Transaction [type] = proto[
                amount : decimal,
                incr   : fn[Transaction, unit],
                proto  : Listing1.Account
            ]

            test_trans [: Transaction]
            def _():
                amount = 36.50
                def incr(self): self.amount += 1
                proto = Listing1.test_account

            test_trans.incr() # self passed automatically
            print(test_trans.name)

        return Listing9
        # TODO decimal intro
        # TODO proto intro
        # TODO proto dispatch
        # TODO proto attribute access

    @pytest.fixture
    def Listing10(self):
        @component
        def Listing10():
            # TODO device selection code
            # make numpy array + send to device
            x [: array[f64]] = [1, 2, 3, 4]
            d_x = to_device(x)

            # define a typed data-parallel OpenCL kernel
            @kernel
            def add5(x : buffer[f64]):
                gid = get_global_id(0) # OpenCL primitive
                x[gid] = x[gid] + 5

            # spawn one device thread per element and run
            add5(d_x, global_size=d_x.length)

            y = d_x.from_device() # retrieve from device
            print(y.to_string()) # prints [6. 7, 8, 9]
        
        return Listing10
        # TODO imports in translation
        # TODO numpy number logic
        # TODO numpy array logic
        # TODO opencl device selection API
        # TODO opencl device transfer API
        # TODO opencl kernels
        # TODO opencl get_global_id primitive
        # TODO opencl buffer lookup
        # TODO opencl add
        # TODO opencl buffer assignment
        # TODO opencl kernel call
        # TODO numpy to_string

