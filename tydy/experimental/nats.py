"""Natural numbers, modularly.

This is aspirational -- a lot of the features used below haven't been implemented yet.
"""
from .. import *
from . import boolean, opt, num

@component
def Nats():
    case_rules(+t, +a) == {
        zero : +a,
        succ : +t > +a
    }
    
    @interface
    def INat():
        t      [type]
        zero   [: t]
        succ   [: t > t]
        case   [: t * case_rules(t, +a) > +a]
        eq     [: t * t > boolean]
        of_num [: num > opt(t)]
        to_num [: t > num]

    @INat
    def NumNat():
        t == num
        zero = 0
        succ = _ [: num] + 1
        
        def case(n, rules):
            if n == 0: rules.zero
            else: rules.succ(n - 1)
        
        def eq(n1, n2):
            n1 == n2
        
        def of_num(n):
            if n < 0: None
            else: Some(n)
        
        def to_num(n): 
            n

    @INat
    def UnaryNat():
        t == Z + S(t)
        
        zero = Z
        succ = S(_)
        
        def case(n, rules):
            match[n]
            with Z: rules.zero
            with S(p): rules.succ(p)
        
        def eq(*n):
            match[n]
            with (Z, Z): True
            with (Z, _): False
            with (S(p1), S(p2)): eq(p1, p2)
            with (_, _): False
        
        def of_num(n):
            if n < 0: None
            else: Some(S(of_num(n - 1)))
        
        def to_num(n):
            match[n]
            with Z: 0
            with S(p): to_num(p) + 1

@component
def TestNats():
    @component
    def TestINat(N):
        Nat.INat > _
        assert N.zero.succ.succ.succ.to_num == 3
        assert {N.of_num(3)} is {Some(_): True, None: False}
        assert {N.of_num(-4)} is {Some(_): False, None: True}
        assert {N.of_num(3), N.of_num(4)} is {(Some(three), Some(four)): three != four, _: False}

    TestINat(Nats.NumNat)
    TestINat(Nats.UnaryNat)

