"""typy numeric types"""
import ast 

import typy
import typy.util as _util
import typy.util.astx as astx

import _boolean
import _fn

# 
# num
#

class num_(typy.Type):
    @classmethod
    def init_idx(cls, idx):
        if idx != ():
            raise typy.TypeFormationError("Index of num_ type must be ().")
        return idx

    @classmethod
    def init_inc_idx(cls, inc_idx):
        if inc_idx != () and inc_idx != Ellipsis:
            raise typy.TypeFormationError("Incomplete index of num_ type must be () or Ellipsis.")
        return inc_idx

    def anon_to_str(self):
        return "num"

    def ana_Num(self, ctx, e):
        n = e.n
        if not isinstance(n, (int, long)):
            raise typy.TypeError("Expression is not an int or long literal.", e)

    @classmethod
    def syn_idx_Num(cls, ctx, e, inc_idx):
        n = e.n
        if isinstance(n, (int, long)):
            return ()
        else:
            raise typy.TypeError("Expression is not an int or long literal.", e)

    def translate_Num(self, ctx, e):
        return astx.copy_node(e)

    def ana_pat_Num(self, ctx, pat):
        n = pat.n 
        if not isinstance(n, (int, long)):
            raise typy.TypeError("Pattern for type 'num' must be int or long.", pat)
        return _util.odict()

    def translate_pat_Num(self, ctx, pat, scrutinee_trans):
        scrutinee_trans_copy = astx.copy_node(scrutinee_trans)
        comparator = astx.copy_node(pat)
        condition = ast.Compare(
            left=scrutinee_trans_copy,
            ops=[ast.Eq()],
            comparators=[comparator])
        return (condition, _util.odict())

    def syn_UnaryOp(self, ctx, e):
        if not isinstance(e.op, ast.Not):
            return self
        else:
            raise typy.TypeError(
                "Invalid unary operator 'not' for operand of type num.", e)

    def translate_UnaryOp(self, ctx, e):
        translation = astx.copy_node(e)
        translation.operand = ctx.translate(e.operand)
        return translation

    def syn_BinOp(self, ctx, e):
        op = e.op
        if isinstance(op, ast.Div):
            ctx.ana(e.right, ieee)
            return ieee
        else:
            ctx.ana(e.right, self)
            return self

    def translate_BinOp(self, ctx, e):
        translation = astx.copy_node(e)
        translation.left = ctx.translate(e.left)
        translation.right = ctx.translate(e.right)
        return translation

    def syn_Compare(self, ctx, e):
        left, ops, comparators = e.left, e.ops, e.comparators
        for op in ops:
            if isinstance(op, (ast.In, ast.NotIn)):
                raise typy.TypeError("Type num does not support this operator.", op)
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

    def syn_Attribute(self, ctx, e):
        attr = e.attr
        if attr == 'f':
            return ieee
        elif attr == 'c':
            return cplx
        else:
            raise typy.TypeError("Invalid attribute.", e)

    def translate_Attribute(self, ctx, e):
        value, attr = e.value, e.attr
        if attr == 'f':
            name = 'float'
        elif attr == 'c':
            name = 'complex'

        return ast.copy_location(
            astx.builtin_call(name, [ctx.translate(value)]),
            value)

num = num_[()]

#
# ieee
# 

class ieee_(typy.Type):
    def __str__(self):
        return "ieee"

    @classmethod
    def init_idx(cls, idx):
        if idx != ():
            raise typy.TypeFormationError("Index of ieee_ type must be ().")
        return idx

    @classmethod
    def init_inc_idx(cls, inc_idx):
        if inc_idx != () and inc_idx != Ellipsis:
            raise typy.TypeFormationError("Incomplete index of ieee_ type must be () or Ellipsis.")
        return inc_idx

    def ana_Num(self, ctx, e):
        if not isinstance(e.n, (int, long, float)):
            raise typy.TypeError(
                "cplx literal cannot be used to introduce value of type 'ieee'.", e)

    @classmethod
    def syn_idx_Num(cls, ctx, e, inc_idx):
        if not isinstance(e.n, (int, long, float)):
            raise typy.TypeError(
                "cplx literal cannot be used to introduce value of type 'ieee'.", e)
        return ()

    def translate_Num(self, ctx, e):
        translation = astx.copy_node(e)
        translation.n = float(e.n)
        return translation

    def ana_pat_Num(self, ctx, pat):
        if not isinstance(pat.n, (int, long, float)):
            raise typy.TypeError(
                "Complex literal cannot be used as a pattern for type 'ieee'.", pat)
        return _util.odict()
    
    def translate_pat_Num(self, ctx, pat, scrutinee_trans):
        n = pat.n
        comparator = astx.copy_node(pat)
        comparator.n = float(n)
        condition = ast.Compare(
            left=scrutinee_trans,
            ops=[ast.Eq()],
            comparators=[comparator])
        return (condition, _util.odict())

    def ana_Name_constructor(self, ctx, e):
        id = e.id
        if id == "NaN" or id == "Inf":
            return
        else:
            raise typy.TypeError("Invalid constructor name: " + id, e)

    @classmethod
    def syn_idx_Name_constructor(cls, ctx, e, inc_idx):
        id = e.id 
        if id == "NaN" or id == "Inf":
            return ()
        else:
            raise typy.TypeError("Invalid constructor name: " + id, e)

    def translate_Name_constructor(self, ctx, e):
        id = e.id
        argument = ast.Str(s=id)
        return astx.builtin_call("float", [argument])

    def ana_pat_Name_constructor(cls, ctx, pat):
        id = pat.id
        if id == "NaN" or id == "Inf":
            return _util.odict()
        else:
            raise typy.TypeError("Invalid constructor name: " + id, pat)

    def translate_pat_Name_constructor(cls, ctx, pat, scrutinee_trans):
        id = pat.id
        if id == "NaN":
            condition = astx.method_call(
                astx.import_expr('math'),
                'isnan',
                [scrutinee_trans])
        else:
            condition = ast.Compare(
                left=scrutinee_trans,
                ops=[ast.Eq()],
                comparators=[
                    astx.builtin_call("float", [ast.Str(s=id)])]
            )
        return (condition, _util.odict())

    def ana_Unary_Name_constructor(self, ctx, e):
        id = e.operand.id
        if id != "Inf":
            raise typy.TypeError("Invalid ieee literal.", e)
        if not isinstance(e.op, (ast.UAdd, ast.USub)):
            raise typy.TypeError("Invalid unary operator on ieee literal.", e)

    @classmethod
    def syn_idx_Unary_Name_constructor(cls, ctx, e, inc_idx):
        id = e.operand.id
        if id != "Inf":
            raise typy.TypeError("Invalid ieee literal.", e)
        if not isinstance(e.op, (ast.UAdd, ast.USub)):
            raise typy.TypeError("Invalid unary operator on ieee literal.", e)
        return ()

    def translate_Unary_Name_constructor(self, ctx, e):
        if isinstance(e.op, ast.UAdd):
            argument = "Inf"
        else:
            argument = "-Inf"
        return astx.builtin_call("float", [ast.Str(s=argument)])

    def ana_pat_Unary_Name_constructor(self, ctx, pat):
        id = pat.operand.id
        if id != "Inf":
            raise typy.TypeError("Invalid ieee literal pattern.", pat)
        if not isinstance(pat.op, (ast.UAdd, ast.USub)):
            raise typy.TypeError(
                "Invalid unary operator on ieee literal pattern.", pat)
        return _util.odict()

    def translate_pat_Unary_Name_constructor(self, ctx, pat, scrutinee_trans):
        if isinstance(pat.op, ast.USub):
            s = "-Inf"
        else:
            s = "Inf"
        condition = ast.Compare(
            left=scrutinee_trans,
            ops=[ast.Eq()],
            comparators=[
                astx.builtin_call("float", [ast.Str(s=s)])]
        )
        return (condition, _util.odict())

    def syn_UnaryOp(self, ctx, e):
        if isinstance(e.op, (ast.Not, ast.Invert)):
            raise typy.TypeError("Invalid unary operator for operand of type ieee.", e)
        else:
            return self
            
    def translate_UnaryOp(self, ctx, e):
        translation = astx.copy_node(e)
        translation.operand = ctx.translate(e.operand)
        return translation

    def syn_BinOp(self, ctx, e):
        if isinstance(e.op, (ast.LShift, ast.RShift, ast.BitOr, ast.BitXor, ast.BitAnd)):
            raise typy.TypeError("Cannot use bitwise operators on ieee values.", e)
        ctx.ana(e.right, self)
        return self

    def translate_BinOp(self, ctx, e):
        translation = astx.copy_node(e)
        translation.left = ctx.translate(e.left)
        translation.right = ctx.translate(e.right)
        return translation

    def syn_Compare(self, ctx, e):
        left, ops, comparators = e.left, e.ops, e.comparators
        for op in ops:
            if isinstance(op, (ast.In, ast.NotIn)):
                raise typy.TypeError("Type ieee does not support this operator.", op)
        for e_ in _util.tpl_cons(left, comparators):
            if hasattr(e_, 'match'): 
                continue # already synthesized
            ctx.ana(e_, self)
        return _boolean.boolean

    def translate_Compare(self, ctx, e):
        translation = astx.copy_node(e)
        translation.left = ctx.translate(e.left)
        translation.comparators = (
            ctx.translate(comparator)
            for comparator in e.comparators)
        return translation

    def syn_Attribute(self, ctx, e):
        if e.attr == 'c':
            return cplx
        else:
            raise typy.TypeError("Invalid attribute.", e)

    def translate_Attribute(self, ctx, e):
        value = e.value
        return ast.copy_location(
            astx.builtin_call('complex', [ctx.translate(value)]),
            value)
ieee = ieee_[()]

#
# cplx
#

class cplx_(typy.Type):
    def __str__(self):
        return "cplx"

    @classmethod
    def init_idx(cls, idx):
        if idx != ():
            raise typy.TypeFormationError("Index of cplx_ type must be ().")
        return idx

    @classmethod
    def init_inc_idx(cls, inc_idx):
        if inc_idx != () and inc_idx != Ellipsis:
            raise typy.TypeFormationError("Incomplete index of cplx_ type must be () or Ellipsis.")
        return inc_idx

    def ana_Num(self, ctx, e):
        # all number literals are valid
        return

    @classmethod
    def syn_idx_Num(cls, ctx, e, inc_idx):
        return ()

    def translate_Num(self, ctx, e):
        translation = astx.copy_node(e)
        n = e.n
        if not isinstance(n, complex):
            translation.n = complex(n)
        return translation

    def ana_pat_Num(self, ctx, pat):
        return _util.odict()

    def translate_pat_Num(self, ctx, pat, scrutinee_trans):
        scrutinee_trans_copy = astx.copy_node(scrutinee_trans)
        comparator = astx.copy_node(pat)
        n = pat.n
        if not isinstance(n, complex):
            comparator.n = complex(n)
        condition = ast.Compare(
            left=scrutinee_trans_copy,
            ops=[ast.Eq()],
            comparators=[comparator])
        return (condition, _util.odict())

    @classmethod
    def _process_Tuple(cls, ctx, e):
        elts = e.elts
        if len(elts) != 2:
            raise typy.TypeError(
                "Using a tuple to introduce a value of type cplx requires two elements.",
                e)
        rl, im = elts[0], elts[1]

        if isinstance(rl, ast.Num):
            ctx.ana(rl, ieee)
        else:
            rl_ty = ctx.syn(rl)
            if rl_ty != num and rl_ty != ieee:
                raise typy.TypeError(
                    "Real component must be be num or ieee.", rl)

        if not isinstance(im, ast.Num):
            im_ty = ctx.syn(im)
            if im_ty != num and im_ty != ieee:
                raise typy.TypeError(
                    "Imaginary component must be a complex literal, or an expressin of type 'num' or 'ieee'.", # noqa
                    im)

    def ana_Tuple(self, ctx, e):
        cplx_._process_Tuple(ctx, e)

    @classmethod
    def syn_idx_Tuple(cls, ctx, e, inc_idx):
        cplx_._process_Tuple(ctx, e)
        return ()

    def translate_Tuple(self, ctx, e):
        elts = e.elts
        rl, im = elts[0], elts[1]

        rl_trans = ctx.translate(rl)

        if isinstance(im, ast.Num):
            n = im.n
            if isinstance(n, complex):
                n = n.imag
            im_trans = ast.copy_location(
                ast.Num(n), 
                im)
        else:
            im_trans = ctx.translate(im)

        # __builtin__.complex([[rl_trans]], [[im_trans]])
        return ast.copy_location(
            astx.builtin_call('complex', [rl_trans, im_trans]), 
            e)

    def ana_pat_Tuple(self, ctx, pat):
        elts = pat.elts
        if len(elts) != 2:
            raise typy.TypeError(
                "Using a tuple pattern for a value of type cplx requires two elements.",
                pat)
        rl, im = elts[0], elts[1]
        rl_bindings = ctx.ana_pat(rl, ieee)
        im_bindings = ctx.ana_pat(im, ieee)
        n_rl_bindings = len(rl_bindings)
        n_im_bindings = len(im_bindings)
        bindings = _util.odict(rl_bindings)
        bindings.update(im_bindings)
        n_bindings = len(bindings)
        if n_bindings != n_rl_bindings + n_im_bindings:
            raise typy.TypeError("Duplicated variables in pattern.", pat)
        return bindings
    
    def translate_pat_Tuple(self, ctx, pat, scrutinee_trans):
        elts = pat.elts
        rl, im = elts[0], elts[1]
        rl_scrutinee_trans = astx.make_Attribute(scrutinee_trans, 'real')
        im_scrutinee_trans = astx.make_Attribute(scrutinee_trans, 'imag')
        (rl_cond, rl_binding_translations) = ctx.translate_pat(rl, rl_scrutinee_trans)
        (im_cond, im_binding_translations) = ctx.translate_pat(im, im_scrutinee_trans)

        condition = astx.make_binary_And(rl_cond, im_cond)

        binding_translations = _util.odict(rl_binding_translations)
        binding_translations.update(im_binding_translations)

        return condition, binding_translations

    def syn_UnaryOp(self, ctx, e):
        if not isinstance(e.op, (ast.Not, ast.Invert)):
            return self
        else:
            raise typy.TypeError("Invalid unary operator for operand of type cplx.", e)

    def translate_UnaryOp(self, ctx, e):
        translation = astx.copy_node(e)
        translation.operand = ctx.translate(e.operand)
        return translation

    def syn_BinOp(self, ctx, e):
        if isinstance(e.op, (ast.LShift, ast.RShift, ast.BitOr, ast.BitXor, ast.BitAnd)):
            raise typy.TypeError("Cannot use bitwise operators on cplx values.", e)
        if isinstance(e.op, ast.Mod):
            raise typy.TypeError("Cannot take the modulus of a complex number.", e)

        right = e.right
        ctx.ana(right, self)

        return self

    def translate_BinOp(self, ctx, e):
        translation = astx.copy_node(e)
        translation.left = ctx.translate(e.left)
        translation.right = ctx.translate(e.right)
        return translation

    def syn_Compare(self, ctx, e):
        left, ops, comparators = e.left, e.ops, e.comparators
        for op in ops:
            if isinstance(op, (ast.Lt, ast.LtE, ast.Gt, ast.GtE)):
                raise typy.TypeError("No ordering relation on complex numbers.", e)
            elif isinstance(op, (ast.In, ast.NotIn)):
                raise typy.TypeError("Type complex does not support this operator.", op)
        for e_ in _util.tpl_cons(left, comparators):
            if hasattr(e_, 'match'): 
                continue # already synthesized
            ctx.ana(e_, self)
        return _boolean.boolean

    def translate_Compare(self, ctx, e):
        translation = astx.copy_node(e)
        translation.left = ctx.translate(e.left)
        translation.comparators = (
            ctx.translate(comparator)
            for comparator in e.comparators)
        return translation

    def syn_Attribute(self, ctx, e):
        attr = e.attr
        if attr == "real" or attr == "imag":
            return ieee
        elif attr == "conjugate":
            return _fn.fn[(), self]
        else:
            raise typy.TypeError("Invalid attribute: " + attr, e)

    def translate_Attribute(self, ctx, e):
        translation = astx.copy_node(e)
        translation.value = ctx.translate(e.value)
        return translation

cplx = cplx_[()]

# MAYBE: ~x on complex equivalent to x.conjugate()?
# MAYBE: x.conj equivalent to x.conjugate?
# TODO: float to integer helper?
# TODO: expose .bitwidth method of int
# TODO: wrap builtin functions
