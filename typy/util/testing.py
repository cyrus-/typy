"""Test utilities."""
import textwrap

import astunparse

def trans_str(a):
    return astunparse.unparse(a)
    
def trans_truth(b):
    return textwrap.dedent(b) + "\n"

def ast_eq(a, b, print_a=False, print_b=False):
    a_s = astunparse.unparse(a)
    b_s = textwrap.dedent(b) + "\n"
    result = a_s == b_s
    if (not result) or print_a:
        print(a_s)
    if print_b:
        print(b_s)
    return result

