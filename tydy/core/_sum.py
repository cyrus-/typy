"""type sum types"""
import ast

import six

import typy
import typy.util as _util

import _product

# 
# finsum
# 

class finsum(typy.Type):
    """Finite sum types.
    
    Examples:
    
      finsum[()] # no variants (uninhabited)
      finsum['A': num] # one variant labeled A with payload type num
      finsum['A': num, 'B': num] # two variants, labeled A and B, both with payload type num
      finsum['A': num, 'B'] == finsum['A': num, 'B': unit]
    """
    @classmethod
    def init_idx(cls, idx):
        return cls._normalize_user_idx(idx)

    @classmethod
    def _normalize_user_idx(cls, provided_idx):
        if not isinstance(provided_idx, tuple):
            provided_idx = (provided_idx,)
        idx = _util.odict()
        for item in provided_idx:
            if isinstance(item, six.string_types):
                lbl, ty = (item, _product.unit)
            elif isinstance(item, slice):
                lbl, ty = item.start, item.stop
                if item.step is not None:
                    raise typy.TypeFormationError(
                        "Invalid variant: " + str(lbl))
            else:
                raise typy.TypeFormationError(
                    "Invalid variant definition.")

            if(not isinstance(lbl, six.string_types) 
            or not typy._is_Name_constructor_id(lbl)):
                raise typy.TypeFormationError(
                    "Label '" + str(lbl) + "' is not a non-empty string with initial capital.")
            if lbl in idx:
                raise typy.TypeFormationError(
                    "Duplicate label '" + lbl + "'.")
            if not isinstance(ty, typy.Type):
                raise typy.TypeFormationError(
                    "Payload for label '" + lbl + "' is not a type.")
            idx[lbl] = ty
        return idx

    @classmethod
    def init_inc_idx(cls, inc_idx):
        raise typy.TypeFormationError("finsum types cannot be incomplete.")

    def anon_to_str(self):
        return "finsum[" + str.join(", ", (
            "'" + lbl + (
                ("': " + str(ty)) if ty != _product.unit else "'")
            for lbl, ty in self.idx.iteritems()
        )) + "]"

    def ana_Name_constructor(self, ctx, e):
        idx = self.idx
        lbl = e.id

        try:
            ty = idx[lbl]
        except KeyError:
            raise typy.TypeError(
                "Label not found in finsum: " + lbl, e)
        if ty != _product.unit:
            raise typy.TypeError(
                "Label has non-unit type but no payload was applied: " + lbl, e)

    def ana_pat_Name_constructor(self, ctx, pat):
        idx = self.idx
        lbl = pat.id

        try:
            ty = idx[lbl]
        except KeyError:
            raise typy.TypeError(
                "Label not found in finsum: " + lbl, pat)
        if ty != _product.unit:
            raise typy.TypeError(
                "Label has non-unit type but no payload pattern was applied: " + lbl, pat)
        return _util.odict()

    def translate_Name_constructor(self, ctx, e):
        lbl = e.id
        return ast.Str(s=lbl)

    def translate_pat_Name_constructor(self, ctx, pat, scrutinee_trans):
        lbl = pat.id
        condition = ast.Compare(
            left=scrutinee_trans,
            ops=[ast.Eq()],
            comparators=[ast.Str(s=lbl)])
        return condition, _util.odict()
    
    def ana_Call_constructor(self, ctx, e):
        if e.starargs is not None:
            raise typy.TypeError("No support for starargs", e)
        if e.kwargs is not None:
            raise typy.TypeError("No support for kwargs", e)
        if len(e.keywords) != 0:
            raise typy.TypeError("No support for keyword arguments.", e)

        idx = self.idx
        lbl = e.func.id

        try:
            ty = idx[lbl]
        except KeyError:
            raise typy.TypeError(
                "Label not found in finsum: " + lbl, e)

        # TODO: special case tpl

        args = e.args
        if len(args) != 1:
            raise typy.TypeError(
                "Must provide a single argument.", e)
        arg = args[0]
        ctx.ana(arg, ty)

    def ana_pat_Call_constructor(self, ctx, pat):
        if pat.starargs is not None:
            raise typy.TypeError("No support for starargs", pat)
        if pat.kwargs is not None:
            raise typy.TypeError("No support for kwargs", pat)
        if len(pat.keywords) != 0:
            raise typy.TypeError("No support for keyword arguments.", pat)

        idx = self.idx
        lbl = pat.func.id

        try:
            ty = idx[lbl]
        except KeyError:
            raise typy.TypeError(
                "Label not found in finsum: " + lbl, pat)
        
        # TODO: special case tpl

        args = pat.args
        if len(args) != 1:
            raise typy.TypeError(
                "Must provide a single argument.", pat)
        arg = args[0]
        return ctx.ana_pat(arg, ty)

    def translate_Call_constructor(self, ctx, e):
        lbl = e.func.id
        arg = e.args[0]
        arg_translation = ctx.translate(arg)
        return ast.Tuple(
            elts=[ast.Str(s=lbl), arg_translation]
        )

    def translate_pat_Call_constructor(self, ctx, pat, scrutinee_trans):
        lbl = pat.func.id

        tag_loc = ast.Subscript(
            value=scrutinee_trans,
            slice=ast.Index(value=ast.Num(n=0)))
        lbl_condition = ast.Compare(
            left=tag_loc,
            ops=[ast.Eq()],
            comparators=[ast.Str(s=lbl)])
        
        arg = pat.args[0]
        arg_scrutinee = ast.Subscript(
            value=scrutinee_trans,
            slice=ast.Index(value=ast.Num(n=1)))
        arg_condition, binding_translations = ctx.translate_pat(arg, arg_scrutinee)

        condition = ast.BoolOp(
            op=ast.And(),
            values=[lbl_condition, arg_condition])

        return condition, binding_translations

