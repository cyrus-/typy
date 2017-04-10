"""tydy errors"""

import typy

class TydyInternalError(Exception): pass

TyError = typy.TyError
TypeFormationError = typy.TypeFormationError
KindError = typy.KindError

