"""typy string types"""
import ast 

import typy
import typy.util as _util
import typy.util.astx as astx

import _boolean
import _numeric

class string_(typy.Type):
    @classmethod
    def init_idx(cls, idx):
        if idx != ():
            raise typy.TypeFormationError("Index of float_ type must be ().")
        return idx

    @classmethod
    def init_inc_idx(cls, inc_idx):
        if inc_idx != () and inc_idx != Ellipsis:
            raise typy.TypeFormationError("Incomplete index of float_ type must be () or Ellipsis.")
        return inc_idx

    def anon_to_str(self):
        return "string"

    def ana_Str(self, ctx, e):
        return # all string literals are ok

    @classmethod
    def syn_idx_Str(cls, ctx, e, inc_idx):
        return ()

    def translate_Str(self, ctx, e):
        return astx.copy_node(e)

    def ana_pat_Str(self, ctx, pat):
        return _util.odict()

    def translate_pat_Str(self, ctx, pat, scrutinee_trans):
        scrutinee_trans_copy = astx.copy_node(scrutinee_trans)
        pat_copy = astx.copy_node(pat)
        condition = ast.Compare(
            left=scrutinee_trans_copy,
            ops=[ast.Eq()],
            comparators=[pat_copy])
        return (condition, _util.odict())

    def syn_BinOp(self, ctx, e):
        op = e.op
        if isinstance(op, ast.Add):
            ctx.ana(e.right, self)
            return self
        else:
            raise typy.TypeError("Invalid binary operator on strings.", e)

    def translate_BinOp(self, ctx, e):
        translation = astx.copy_node(e)
        translation.left = ctx.translate(e.left)
        translation.right = ctx.translate(e.right)
        return translation

    def syn_Compare(self, ctx, e):
        left, ops, comparators = e.left, e.ops, e.comparators
        for op in ops:
            if not isinstance(op, (ast.Eq, ast.NotEq, ast.Is, ast.IsNot, ast.In, ast.NotIn)):
                raise typy.TypeError("Invalid comparison operator on strings.", e)
        for e_ in _util.tpl_cons(left, comparators):
            if hasattr(e_, 'match'): 
                continue # already synthesized
            ctx.ana(e_, self)
        return _boolean.boolean

    def translate_Compare(self, ctx, e):
        translation = astx.copy_node(e)
        translation.left = ctx.translate(e.left)
        translation.comparators = tuple(
            ctx.translate(comparator)
            for comparator in e.comparators)
        return translation

    def syn_Subscript(self, ctx, e):
        slice_ = e.slice 
        if isinstance(slice_, ast.Ellipsis):
            raise typy.TypeError("stringing slice cannot be an Ellipsis.", e)
        elif isinstance(slice_, ast.ExtSlice):
            raise typy.TypeError("stringing slice can only have one dimension.", e)
        elif isinstance(slice_, ast.Index):
            ctx.ana(slice_.value, _numeric.num)
        else: # if isinstance(slice_, ast.Slice):
            lower, upper, step = slice_.lower, slice_.upper, slice_.step
            if lower is not None:
                ctx.ana(lower, _numeric.num)
            if upper is not None:
                ctx.ana(upper, _numeric.num)
            if not _is_None(step):
                ctx.ana(step, _numeric.num)
        return self

    def translate_Subscript(self, ctx, e):
        translation = astx.copy_node(e)
        translation.value = ctx.translate(e.value)
        slice_ = e.slice
        slice_translation = astx.copy_node(slice_)
        if isinstance(slice_, ast.Index):
            slice_translation.value = ctx.translate(slice_.value)
        else:
            lower, upper, step = slice_.lower, slice_.upper, slice_.step
            slice_translation.lower = ctx.translate(lower) if lower is not None else None
            slice_translation.upper = ctx.translate(upper) if upper is not None else None
            if not _is_None(step):
                slice_translation.step = ctx.translate(step)
            else:
                slice_translation.step = None
        translation.slice = slice_translation
        return translation 

def _is_None(node):
    #
    # for some reason, 
    #
    #   > ast.dump(ast.parse(x[0:1:]))
    #   Module(body=[Expr(value=Subscript(value=Name(id='x', ctx=Load()), 
    #       slice=Slice(lower=Num(n=0), upper=None, 
    #       step=Name(id='None', ctx=Load())), ctx=Load()))])
    #
    # notice that the step value is not 'None' but the Name that contains 'None'. 
    # Need to special case this.
    #
    return node is None or (isinstance(node, ast.Name) and node.id == 'None')

string = string_[()]

