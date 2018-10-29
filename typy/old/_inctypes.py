"""typy incomplete types"""
import _errors
import _typelevel 

__all__ = ('IncompleteType',)

class IncompleteType(object): # TODO Is this a type expression? I think so.
    """Represents an incomplete type, used for literal forms.

    An incomplete type is constructed by providing an index 
    containing one or more ellipses:
        tycon[a, ..., b]
    """
    @staticmethod
    def _construct_nonrecursive(tycon, inc_idx, shortname=None):
        inc_idx = tycon.init_inc_idx(inc_idx)
        return IncompleteType(tycon, inc_idx, shortname, None,
                              from_construct_incty=True)

    @staticmethod
    def _construct_equirec_incty(tycon, equirec_idx_schema, shortname):
        inc_ty = IncompleteType(tycon, None, equirec_idx_schema, 
                                from_construct_incty=True)
        provided_inc_idx_unfolded = equirec_idx_schema(inc_ty)
        inc_ty.inc_idx = tycon.init_inc_idx(provided_inc_idx_unfolded)
        return inc_ty

    def __init__(self, tycon, inc_idx, shortname, equirec_idx_schema, 
                 from_construct_incty=False):
        if not from_construct_incty:
            raise _errors.TypeFormationError(
                "Incomplete types should not be constructed directly. Use tycon[idx].")
        self.tycon = tycon
        self.inc_idx = inc_idx
        self.shortname = shortname
        self.equirec_idx_schema = equirec_idx_schema

    def __call__(self, f):
        if issubclass(self.tycon, FnType):
            (ast, static_env) = _reflect_func(f)
            return Fn(ast, static_env, self)
        else: 
            raise _errors.TyError(
                "Incomplete non-FnType used as a top-level function decorator.",
                None)

    def __eq__(self, other):
        return isinstance(other, IncompleteType) \
            and _typelevel.tycon(self) is _typelevel.tycon(other) \
            and self.inc_idx == other.inc_idx

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        shortname = self.shortname
        if shortname is not None:
            return shortname
        else:
            return self.tycon.anon_inc_to_str(self.inc_idx)

    def __repr__(self):
        return self.__str__()


