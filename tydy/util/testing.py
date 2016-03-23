"""Test utilities."""
import textwrap

import astunparse

def translation_eq(f, truth, print_f=False):
    """helper function for test_translate functions

    compares an AST to the string truth, which should contain Python code.
    truth is first dedented.
    """
    f.compile()
    translation = f.translation
    translation_s = astunparse.unparse(translation)
    if print_f:
        print translation_s
    truth_s = "\n" + textwrap.dedent(truth) + "\n"
    assert translation_s == truth_s
