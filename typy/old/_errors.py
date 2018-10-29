"""typy errors"""

# indentation indicates inheritance relationshipi
__all__ = (
    "TypyException",
        "StaticError",
            "TyError",
                "TypeMismatchError",
                "OpNotSupported",
            "KindError",
            "TypeFormationError",
            "KindFormationError",
        "FragmentError", 
            "OpTranslationLogicMissing",
            "OpInvalid",
        "FragmentCannotBeInstantiated") # noqa

class TypyException(Exception): 
    """Base class for typy exceptions."""

class StaticError(TypyException):
    """Base class for errors detected statically in user programs."""

class TyError(StaticError):
    """Type errors in user programs."""
    def __init__(self, message, tree):
        StaticError.__init__(self, message)
        self.tree = tree

class TypeMismatchError(TyError):
    """Type error where the expected type did not match synthesized type."""
    def __init__(self, expected, got, tree):
        TyError.__init__(self, 
            "Type mismatch. Expected: {0}. Got: {1}.".format(expected, got), 
            tree)
        self.expected = expected
        self.got = got

class OpNotSupported(TyError):
    """Type error indicating that an operator that is not supported by the 
    delegated fragment was used."""
    def __init__(self, delegate, meth_category, meth_name, informal_name, tree):
        TyError.__init__(self, informal_name + " not supported.", tree)
        self.delegate = delegate
        self.meth_category = meth_category
        self.meth_name = meth_name
        self.informal_name = informal_name
        self.tree = tree

class KindError(StaticError):
    """Kind errors in user programs."""
    def __init__(self, message):
        TypyException.__init__(self, message)

class KindFormationError(StaticError):
    pass

class TypeFormationError(StaticError):
    pass

class FragmentError(TypyException):
    """An invariant was violated by a fragment."""
    pass

class OpTranslationLogicMissing(FragmentError):
    def __init__(self, delegate, meth_category, meth_name, informal_name, tree):
        FragmentError.__init__(self, informal_name + " not supported.")
        self.delegate = delegate
        self.meth_category = meth_category
        self.meth_name = meth_name
        self.informal_name = informal_name
        self.tree = tree

class OpInvalid(FragmentError):
    def __init__(self, message, tree):
        FragmentError.__init__(self, message)
        self.tree = tree

class FragmentCannotBeInstantiated(Exception):
    def __init__(self):
	    Exception.__init__(self, "Fragments cannot be instantiated.")

