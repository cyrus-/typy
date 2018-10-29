"""typy standard library"""
import ast
from collections import OrderedDict

from .. import util as _util 
from ..util import astx
from .._contexts import BlockTransMechanism
from .._fragments import Fragment
from .._ty_exprs import CanonicalTy, TypeKind
from .._errors import TypeValidationError, TyError
from .. import _terms

try:
    integer_types = (int, long)
except NameError:
    integer_types = (int,)

class unit(Fragment):
    @classmethod
    def init_idx(cls, ctx, idx_ast):
        return _check_trivial_idx_ast(idx_ast)

    @classmethod
    def ana_Tuple(cls, ctx, e, idx):
        if len(e.elts) != 0:
            raise TyError(
                "Tuple must be empty to be a unit value.", e)

    @classmethod
    def trans_Tuple(cls, ctx, e, idx):
        return astx.copy_node(e)

    @classmethod
    def ana_pat_Tuple(cls, ctx, pat, idx):
        if len(pat.elts) != 0:
            raise TyError(
                "Tuple pattern must be empty to match unit values.", pat)
        return { }

    @classmethod
    def trans_pat_Tuple(cls, ctx, pat, idx, scrutinee_trans):
        return (ast.copy_location(
            ast.NameConstant(value=True), pat), { })

    @classmethod
    def syn_Compare(cls, ctx, e):
        ctx.ana(e.left, unit_ty)
        for op, comparator in zip(e.ops, e.comparators):
            if isinstance(op, (ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn)):
                raise TyError("Invalid comparison operator on unit.", comparator)
            ctx.ana(comparator, unit_ty)
        return CanonicalTy(boolean, ())
    
    @classmethod
    def trans_Compare(cls, ctx, e):
        left_tr = ctx.trans(e.left)
        comp_trs = [ ]
        for comparator in e.comparators:
            comp_trs.append(ctx.trans(comparator))
        return ast.copy_location(
            ast.Compare(
                left = left_tr,
                ops = e.ops,
                comparators = comp_trs), e)

unit_ty = CanonicalTy(unit, ())

class boolean(Fragment):
    @classmethod
    def init_idx(cls, ctx, idx_ast):
        return _check_trivial_idx_ast(idx_ast)

    @classmethod
    def ana_NameConstant(cls, ctx, e, idx):
        value = e.value
        if value is True or value is False:
            return
        else:
            raise TyError("Invalid name constant: " + str(value), e)

    @classmethod
    def trans_NameConstant(cls, ctx, e, idx):
        return ast.copy_location(
            ast.NameConstant(value=e.value), e)

    @classmethod
    def ana_pat_NameConstant(cls, ctx, pat, idx):
        value = pat.value
        if value is True or value is False:
            return {}
        else:
            raise TyError("Invalid name constant: " + str(value), pat)

    @classmethod
    def trans_pat_NameConstant(cls, ctx, pat, idx, scrutinee_trans):
        if pat.value:
            condition = scrutinee_trans
        else:
            condition = ast.fix_missing_locations(ast.copy_location(
                ast.UnaryOp(
                    op = ast.Not(),
                    operand=scrutinee_trans), pat))
        return condition, {}

    @classmethod
    def syn_BoolOp(cls, ctx, e):
        for value in e.values:
            ctx.ana(value, boolean_ty)
        return boolean_ty

    @classmethod
    def ana_BoolOp(cls, ctx, e, idx):
        for value in e.values:
            ctx.ana(value, boolean_ty)

    @classmethod
    def trans_BoolOp(cls, ctx, e, idx=None):
        values_tr = [ ]
        for value in e.values:
            values_tr.append(ctx.trans(value))
        return ast.copy_location(
            ast.BoolOp(
                op = e.op,
                values = values_tr), e)

    @classmethod
    def syn_Compare(cls, ctx, e):
        ctx.ana(e.left, boolean_ty)
        for op, comparator in zip(e.ops, e.comparators):
            if isinstance(op, (ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn)):
                raise TyError("Invalid comparison operator on unit.", comparator)
            ctx.ana(comparator, boolean_ty)
        return boolean_ty

    @classmethod
    def trans_Compare(cls, ctx, e):
        left_tr = ctx.trans(e.left)
        comp_trs = [ ]
        for comparator in e.comparators:
            comp_trs.append(ctx.trans(comparator))
        return ast.copy_location(
            ast.Compare(
                left = left_tr,
                ops = e.ops,
                comparators = comp_trs), e)

    @classmethod
    def check_If(cls, ctx, stmt, idx):
        cls.syn_If(ctx, stmt, idx)

    @classmethod
    def trans_checked_If(cls, ctx, stmt, mechanism):
        return cls.trans_If(cls, ctx, stmt, mechanism)

    @classmethod
    def syn_If(cls, ctx, e, idx):
        body_block = e.body_block = _terms.Block(e.body)
        body_ty = ctx.syn_block(body_block)
        orelse_block = e.orelse_block = _terms.Block(e.orelse)
        orelse_ty = ctx.ana_block(orelse_block, body_ty)
        return body_ty
    
    @classmethod
    def ana_If(cls, ctx, e, idx, ty):
        body_block = e.body_block = _terms.Block(e.body)
        orelse_block = e.orelse_block = _terms.Block(e.orelse)
        ctx.ana_block(body_block, ty)
        ctx.ana_block(orelse_block, ty)

    @classmethod
    def trans_If(cls, ctx, e, idx, mechanism):
        return [ast.copy_location(
            ast.If(
                test=ctx.trans(e.test),
                body=ctx.trans_block(e.body_block, mechanism),
                orelse=ctx.trans_block(e.orelse_block, mechanism)), e)]

    @classmethod
    def syn_IfExp(cls, ctx, e, idx):
        body_ty = ctx.syn(e.body)
        ctx.ana(e.orelse, body_ty)
        return body_ty

    @classmethod
    def ana_IfExp(cls, ctx, e, idx, ty):
        ctx.ana(e.body, ty)
        ctx.ana(e.orelse, ty)

    @classmethod
    def trans_IfExp(cls, ctx, e, idx):
        return ast.copy_location(
            ast.IfExp(
                test=ctx.trans(e.test),
                body=ctx.trans(e.body),
                orelse=ctx.trans(e.orelse)), e)

boolean_ty = CanonicalTy(boolean, ())

class string(Fragment):
    @classmethod
    def init_idx(cls, ctx, idx_ast):
        return _check_trivial_idx_ast(idx_ast)

    @classmethod
    def ana_Str(cls, ctx, e, idx):
        return

    @classmethod
    def trans_Str(cls, ctx, e, idx):
        return astx.copy_node(e)

    @classmethod
    def ana_pat_Str(cls, ctx, pat, idx):
        return {}

    @classmethod
    def trans_pat_Str(cls, ctx, pat, idx, scrutinee_trans):
        condition = ast.copy_location(
            ast.Compare(
                left=scrutinee_trans,
                ops=[ast.Eq()],
                comparators=[ast.copy_location(
                    ast.Str(s=pat.s),
                    pat)]),
            pat)
        return condition, {}

    @classmethod
    def ana_JoinedStr(cls, ctx, e, idx):
        values = e.values
        for value in values:
            if isinstance(value, ast.Str): continue
            else: # FormattedValue
                if value.conversion != -1:
                    raise TyError(
                        "string types do not support conversions.", value)
                if value.format_spec is not None:
                    raise TyError(
                        "string types do not support format specifications.",
                        value)
                ctx.ana(value.value, string_ty)

    @classmethod
    def trans_JoinedStr(cls, ctx, e, idx):
        return ast.copy_location(
            ast.JoinedStr(
                values=[
                    ast.copy_location(ast.Str(s=value.s), value)
                    if isinstance(value, ast.Str) else 
                    ast.copy_location(
                        ast.FormattedValue(
                            value=ctx.trans(value.value),
                            conversion=value.conversion,
                            format_spec=value.format_spec),
                        value)
                    for value in e.values]),
            e)

    @classmethod
    def ana_pat_JoinedStr(cls, ctx, pat, idx):
        values = pat.values
        before_str = None
        after_str = None
        formatted_pat = None
        for value in values:
            if isinstance(value, ast.Str):
                if formatted_pat is None:
                    before_str = value.s
                else:
                    after_str = value.s
            else: # FormattedValue
                if formatted_pat is None:
                    formatted_pat = value.value
                else:
                    raise TyError(
                        "Can only have one formatted value in format string "
                        "pattern.", value)
                if value.format_spec is not None:
                    raise TyError(
                        "Cannot use format specification in format string "
                        "pattern.", value)
                if value.conversion != -1:
                    raise TyError(
                        "Cannot use conversions in format string pattern.", 
                        value)
        pat.before_str = before_str
        pat.after_str = after_str
        pat.formatted_pat = formatted_pat
        if formatted_pat is not None:
            return ctx.ana_pat(formatted_pat, string_ty)

    @classmethod 
    def trans_pat_JoinedStr(cls, ctx, pat, idx, scrutinee_trans):
        before_str, formatted_pat, after_str = \
            pat.before_str, pat.formatted_pat, pat.after_str
        conditions = []
        min_length = 0
        if before_str is not None:
            min_length += len(before_str)
            before_str_condition = ast.fix_missing_locations(ast.copy_location(
                astx.method_call(
                    scrutinee_trans,
                    "startswith",
                    [ast.Str(s=before_str)]),
                pat))
        else: before_str_condition = None

        if after_str is not None:
            min_length += len(after_str)
            after_str_condition = ast.fix_missing_locations(ast.copy_location(
                astx.method_call(
                    scrutinee_trans,
                    "endswith",
                    [ast.Str(s=after_str)]),
                pat))
        else: after_str_condition = None
        
        if before_str is not None and after_str is not None and min_length > 0:
            length_condition = ast.fix_missing_locations(ast.copy_location(
                ast.Compare(
                    left=astx.builtin_call('len', [scrutinee_trans]),
                    ops=[ast.GtE()], 
                    comparators=[ast.Num(n=min_length)]),
                pat)) # TODO do the other things do length checks properly?
            conditions.append(length_condition)

        if before_str_condition is not None:
            conditions.append(before_str_condition)
            f_lower = ast.Num(n=len(before_str))
        else: f_lower = None
        if after_str_condition is not None:
            conditions.append(after_str_condition)
            f_upper = ast.Num(n=-len(after_str))
        else: f_upper = None

        if f_lower is not None or f_upper is not None:
            formatted_pat_scrutinee = \
                ast.fix_missing_locations(ast.copy_location(
                    ast.Subscript(
                        value=scrutinee_trans,
                        slice=ast.Slice(
                            lower=f_lower,
                            upper=f_upper,
                            step=None),
                        ctx=astx.load_ctx), pat))
        else:
            formatted_pat_scrutinee = scrutinee_trans
        formatted_pat_condition, binding_translations = \
            ctx.trans_pat(formatted_pat, formatted_pat_scrutinee)
        conditions.append(formatted_pat_condition)
        
        if len(conditions) >= 2:
            condition = ast.copy_location(
                ast.BoolOp(
                    op=ast.And(),
                    values=conditions), pat)
        else:
            condition = conditions[0]
        return condition, binding_translations

    @classmethod
    def ana_FormattedValue(cls, ctx, e, idx):
        e.pretend_e = pretend_e = ast.copy_location(
            ast.JoinedStr(
                values=[e]), e)
        cls.ana_JoinedStr(ctx, pretend_e, idx)

    @classmethod
    def trans_FormattedValue(cls, ctx, e, idx):
        return cls.trans_JoinedStr(ctx, e.pretend_e, idx)

    @classmethod
    def ana_pat_FormattedValue(cls, ctx, pat, idx):
        pat.pretend_pat = pretend_pat = ast.copy_location(
            ast.JoinedStr(
                values=[pat]), pat)
        return cls.ana_pat_JoinedStr(ctx, pretend_pat, idx)

    @classmethod
    def trans_pat_FormattedValue(cls, ctx, pat, idx, scrutinee_trans):
        return cls.trans_pat_JoinedStr(ctx, pat.pretend_pat, idx, 
                                       scrutinee_trans)

    @classmethod
    def ana_pat_BinOp(cls, ctx, pat, idx):
        op = pat.op
        if isinstance(op, ast.Add):
            left, right = pat.left, pat.right
            if isinstance(left, ast.Str):
                if left.s == "":
                    raise TyError(
                        "Literal pattern in + pattern must be non-empty.", 
                        left)
                return ctx.ana_pat(right, string_ty)
            elif isinstance(right, ast.Str):
                if right.s == "":
                    raise TyError(
                        "Literal pattern in + pattern must be non-empty.",
                        right)
                return ctx.ana_pat(left, string_ty)
            else:
                raise TyError("One side of + pattern must be a literal.", pat)
        else:
            raise TyError("Invalid pattern operator on strings.", pat)

    @classmethod
    def trans_pat_BinOp(cls, ctx, pat, idx, scrutinee_trans):
        left, right = pat.left, pat.right
        if isinstance(left, ast.Str):
            left_condition = ast.fix_missing_locations(ast.copy_location(
                astx.method_call(
                    scrutinee_trans,
                    "startswith",
                    [left]),
                pat))
            remainder = ast.fix_missing_locations(ast.copy_location(
                ast.Subscript(
                    value=scrutinee_trans,
                    slice=ast.Slice(ast.Num(n=len(left.s)), None, None),
                    ctx=astx.load_ctx),
                pat)) # scrutinee_trans[len(left):]
            right_condition, binding_translations = ctx.trans_pat(right, remainder)
            condition = ast.copy_location(
                astx.make_binary_And(left_condition, right_condition),
                pat)
        else:
            right_condition = ast.fix_missing_locations(ast.copy_location(
                astx.method_call(
                    scrutinee_trans,
                    "endswith",
                    [right]), 
                pat))
            remainder = ast.fix_missing_locations(ast.copy_location(
                ast.Subscript(
                    value=scrutinee_trans,
                    slice=ast.Slice(None, ast.Num(n=-len(right.s)), None),
                    ctx=astx.load_ctx), 
                pat))
            left_condition, binding_translations = ctx.trans_pat(left, remainder)
            condition = ast.copy_location(
                astx.make_binary_And(left_condition, right_condition),
                pat)
        return condition, binding_translations

    @classmethod
    def syn_BinOp(cls, ctx, e):
        left, op, right = e.left, e.op, e.right
        string_ty = CanonicalTy(cls, ())
        if isinstance(op, ast.Add):
            ctx.ana(left, string_ty)
            ctx.ana(right, string_ty)
            return string_ty
        else:
            raise TyError("Invalid string operator.", e)

    @classmethod
    def trans_BinOp(cls, ctx, e):
        return ast.copy_location(
            ast.BinOp(
                left=ctx.trans(e.left),
                op=e.op,
                right=ctx.trans(e.right)),
        e)

    @classmethod
    def syn_Subscript(cls, ctx, e, idx):
        slice = e.slice
        if isinstance(slice, ast.Index):
            ctx.ana(slice.value, num_ty)
            return string_ty
        elif isinstance(slice, ast.Slice):
            lower, upper, step = slice.lower, slice.upper, slice.step
            if lower is not None:
                ctx.ana(lower, num_ty)
            if upper is not None:
                ctx.ana(upper, num_ty)
            if step is not None:
                ctx.ana(step, num_ty)
            return string_ty
        else:
            raise TyError("Invalid string slice.", e)

    @classmethod
    def trans_Subscript(cls, ctx, e, idx):
        slice = e.slice
        if isinstance(slice, ast.Index):
            slice_tr = ast.copy_location(
                ast.Index(value=ctx.trans(slice.value)),
                slice)
        else:
            lower, upper, step = slice.lower, slice.upper, slice.step
            lower_tr = ctx.trans(lower) if lower is not None else None
            upper_tr = ctx.trans(upper) if upper is not None else None
            step_tr = ctx.trans(step) if step is not None else None
            slice_tr = ast.copy_location(
                ast.Slice(lower_tr, upper_tr, step_tr),
                slice)
        return ast.fix_missing_locations(ast.copy_location(
            ast.Subscript(
                value=ctx.trans(e.value),
                slice=slice_tr,
                ctx=e.ctx), 
            e))

    @classmethod
    def syn_Compare(cls, ctx, e):
        left, ops, comparators = e.left, e.ops, e.comparators
        ctx.ana(left, string_ty)
        for op, comparator in zip(ops, comparators):
            if isinstance(op, (ast.In, ast.NotIn)):
                raise TyError("Invalid comparison operator for strings.",
                              comparator)
            ctx.ana(comparator, string_ty)
        return boolean_ty

    @classmethod
    def trans_Compare(cls, ctx, e):
        return ast.fix_missing_locations(ast.copy_location(
            ast.Compare(
                left=ctx.trans(e.left),
                ops=e.ops,
                comparators=[
                    ctx.trans(comparator) 
                    for comparator in e.comparators]),
            e))

string_ty = CanonicalTy(string, ())

class num(Fragment):
    @classmethod
    def init_idx(cls, ctx, idx_ast):
        return _check_trivial_idx_ast(idx_ast)

    @classmethod
    def ana_Num(cls, ctx, e, idx):
        n = e.n
        if isinstance(n, integer_types):
            return
        else:
            raise TyError("Invalid literal for num type.", e)

    @classmethod
    def ana_UnaryOp(cls, ctx, e, idx):
        if isinstance(e.op, ast.Not):
            raise TyError("Invalid unary operator 'not' for num type.", e)
        ctx.ana(e.operand, CanonicalTy(num, ()))

    @classmethod
    def trans_Num(cls, ctx, e, idx):
        return ast.copy_location(
            ast.Num(n=e.n), e)

    @classmethod
    def ana_pat_Num(cls, ctx, pat, idx):
        n = pat.n
        if isinstance(n, integer_types):
            return {}
        else:
            raise TyError("Invalid pattern literal for num type.", pat)

    @classmethod
    def trans_pat_Num(cls, ctx, pat, idx, scrutinee_trans):
        condition = ast.fix_missing_locations(ast.copy_location(
            ast.Compare(
                left = scrutinee_trans,
                ops=[ast.Eq()],
                comparators=[ast.Num(n=pat.n)]), pat))
        return condition, {}

    @classmethod
    def ana_pat_UnaryOp(cls, ctx, pat, idx):
        op = pat.op
        if isinstance(op, (ast.UAdd, ast.USub)):
            return ctx.ana_pat(pat.operand, num_ty)
        else:
            raise TyError("Invalid pattern for num type.", pat)

    @classmethod
    def trans_pat_UnaryOp(cls, ctx, pat, idx, scrutinee_trans):
        if isinstance(pat.op, ast.USub):
            cond_op = ast.Lt()
            new_scrutinee_trans = ast.fix_missing_locations(ast.copy_location(
                ast.UnaryOp(
                    op=ast.USub(),
                    operand=scrutinee_trans), pat))
        else:
            cond_op = ast.Gt()
            new_scrutinee_trans = scrutinee_trans

        this_condition = ast.fix_missing_locations(ast.copy_location(
            ast.Compare(
                left=scrutinee_trans,
                ops=[cond_op],
                comparators=[ast.Num(n=0)]), pat))
        operand_condns, bindings = ctx.trans_pat(pat.operand, 
                                                 new_scrutinee_trans)
        condition = ast.fix_missing_locations(ast.copy_location(
            ast.BoolOp(
                op=ast.And(),
                values=[this_condition, operand_condns]), pat))
        return condition, bindings

    @classmethod
    def syn_BinOp(cls, ctx, e):
        op = e.op
        if isinstance(op, ast.MatMult):
            raise TyError("Invalid operator on numbers.", e)
        else:
            left = e.left
            try:
                ctx.ana(left, num_ty)
                left_ty = num_ty
            except TyError:
                ctx.ana(left, ieee_ty)
                left_ty = ieee_ty
            right = e.right
            try:
                ctx.ana(right, num_ty)
                right_ty = num_ty
            except TyError:
                ctx.ana(right, ieee_ty)
                right_ty = num_ty
            if isinstance(e.op, ast.Div):
                return ieee_ty
            else:
                if left_ty is ieee_ty or right_ty is ieee_ty:
                    return ieee_ty
                else:
                    return num_ty

    @classmethod
    def ana_BinOp(cls, ctx, e):
        if isinstance(e.op, ast.MatMult):
            raise TyError("Invalid operator on numbers.", e)
        elif isinstance(e.op, ast.Div):
            raise TyError("Cannot use division at num type.", e)
        else:
            ctx.ana(e.left, num_ty)
            ctx.ana(e.right, num_ty)

    @classmethod
    def trans_BinOp(cls, ctx, e):
        return ast.copy_location(
            ast.BinOp(
                left=ctx.trans(e.left),
                op=e.op,
                right=ctx.trans(e.right)), e)

    @classmethod
    def syn_UnaryOp(cls, ctx, e, idx):
        if isinstance(e.op, ast.Not):
            raise TyError("Invalid unary operator 'not' for num type.", e)
        return CanonicalTy(num, ())

    @classmethod
    def trans_UnaryOp(cls, ctx, e, idx=None):
        return ast.copy_location(
            ast.UnaryOp(
                op=e.op,
                operand=ctx.trans(e.operand)), e)

    @classmethod
    def syn_Compare(cls, ctx, e):
        left = e.left
        try:
            ctx.ana(left, num_ty)
        except TyError:
            ctx.ana(left, ieee_ty)
        for op, comparator in zip(e.ops, e.comparators):
            if isinstance(op, (ast.In, ast.NotIn)):
                raise TyError(
                    "Invalid comparison operator for num.", 
                    comparator)
            try:
                ctx.ana(comparator, num_ty)
            except TyError:
                ctx.ana(comparator, ieee_ty)
        return boolean_ty

    @classmethod
    def trans_Compare(cls, ctx, e):
        return ast.copy_location(
            ast.Compare(
                left=ctx.trans(e.left),
                ops=e.ops,
                comparators=[
                    ctx.trans(comparator)
                    for comparator in e.comparators]), e)

num_ty = CanonicalTy(num, ())

class ieee(Fragment):
    @classmethod
    def init_idx(cls, ctx, idx_ast):
        return _check_trivial_idx_ast(idx_ast)

    @classmethod
    def ana_Num(cls, ctx, e, idx):
        return

    @classmethod
    def trans_Num(cls, ctx, e, idx):
        return ast.copy_location(
            ast.Num(n=e.n), e)

    @classmethod
    def ana_Name(cls, ctx, e, idx):
        id = e.id
        if id == "NaN" or id == "Inf" or id == "Infinity":
            return
        else:
            raise TyError("Invalid name constant for ieee type.", e)

    @classmethod
    def trans_Name(cls, ctx, e, idx):
        return ast.fix_missing_locations(ast.copy_location(
            astx.builtin_call(
               'float', [ast.Str(s=e.id)]), e))
                               
    @classmethod
    def ana_UnaryOp(cls, ctx, e, idx):
        if isinstance(e.op, (ast.Not, ast.Invert)):
            raise TyError("Invalid unary operator for ieee type.", e)
        ctx.ana(e.operand, CanonicalTy(ieee, ()))

    @classmethod
    def ana_pat_Num(cls, ctx, pat, idx):
        return {}

    @classmethod
    def trans_pat_Num(cls, ctx, pat, idx, scrutinee_trans):
        condition = ast.fix_missing_locations(ast.copy_location(
            ast.Compare(
                left = scrutinee_trans,
                ops=[ast.Eq()],
                comparators=[ast.Num(n=pat.n)]), pat))
        return condition, {}

    @classmethod
    def ana_pat_Name(cls, ctx, pat, idx):
        id = pat.id
        if id == "NaN" or id == "Inf" or id == "Infinity":
            return {}
        else:
            raise TyError("Invalid name constant for ieee type: " + id, pat)

    @classmethod
    def trans_pat_Name(cls, ctx, pat, idx, scrutinee_trans):
        id = pat.id
        if id == "Inf" or id == "Infinity":
            condition = ast.fix_missing_locations(ast.copy_location(
                ast.Compare(
                    left=scrutinee_trans,
                    ops=[ast.Eq()],
                    comparators=[
                        astx.builtin_call('float', [ast.Str(s=pat.id)])]),
                pat))
        else: # NaN
            math = ctx.add_import("math")
            condition = ast.fix_missing_locations(ast.copy_location(
                ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id=math, ctx=astx.load_ctx),
                        attr="isnan",
                        ctx=astx.load_ctx),
                    args=[scrutinee_trans],
                    keywords=[]), pat))
        return condition, {}

    @classmethod
    def ana_pat_UnaryOp(cls, ctx, pat, idx):
        if isinstance(pat.op, (ast.UAdd, ast.USub)):
            return ctx.ana_pat(pat.operand, ieee_ty)
        else:
            raise TyError("Invalid pattern for ieee type.", pat)

    @classmethod
    def trans_pat_UnaryOp(cls, ctx, pat, idx, scrutinee_trans):
        if isinstance(pat.op, ast.USub):
            cond_op = ast.Lt()
            new_scrutinee_trans = ast.fix_missing_locations(ast.copy_location(
                ast.UnaryOp(
                    op=ast.USub(),
                    operand=scrutinee_trans), pat))
        else:
            cond_op = ast.Gt()
            new_scrutinee_trans = scrutinee_trans

        this_condition = ast.fix_missing_locations(ast.copy_location(
            ast.Compare(
                left=scrutinee_trans,
                ops=[cond_op],
                comparators=[ast.Num(n=0.0)]), pat))
        operand_condns, bindings = ctx.trans_pat(pat.operand, 
                                                 new_scrutinee_trans)
        condition = ast.fix_missing_locations(ast.copy_location(
            ast.BoolOp(
                op=ast.And(),
                values=[this_condition, operand_condns]), pat))
        return condition, bindings

    precedence = set([num])

    @classmethod
    def syn_BinOp(cls, ctx, e):
        op = e.op
        if isinstance(op, (ast.MatMult, ast.BitOr, ast.BitXor, 
                           ast.BitAnd, ast.LShift, ast.RShift)):
            raise TyError("Invalid operator on ieee.", e)
        else:
            left = e.left
            try:
                ctx.ana(left, ieee_ty)
            except TyError:
                ctx.ana(left, num_ty)
            right = e.right
            try:
                ctx.ana(right, ieee_ty)
            except TyError:
                ctx.ana(right, num_ty)
            return ieee_ty

    @classmethod
    def ana_BinOp(cls, ctx, e):
        if isinstance(op, (ast.MatMult, ast.BitOr, ast.BitXor, 
                           ast.BitAnd, ast.LShift, ast.RShift)):
            raise TyError("Invalid operator on ieee.", e)
        else:
            left = e.left
            try:
                ctx.ana(left, ieee_ty)
            except TyError:
                ctx.ana(left, num_ty)
            right = e.right
            try:
                ctx.ana(right, ieee_ty)
            except TyError:
                ctx.ana(right, num_ty)

    @classmethod
    def trans_BinOp(cls, ctx, e):
        return ast.copy_location(
            ast.BinOp(
                left=ctx.trans(e.left),
                op=e.op,
                right=ctx.trans(e.right)), e)

    @classmethod
    def syn_UnaryOp(cls, ctx, e, idx):
        if isinstance(e.op, (ast.Not, ast.Invert)):
            raise TyError("Invalid unary operator for ieee type.", e)
        return ieee_ty

    @classmethod
    def trans_UnaryOp(cls, ctx, e, idx=None):
        return ast.copy_location(
            ast.UnaryOp(
                op=e.op,
                operand=ctx.trans(e.operand)), e)

    @classmethod
    def syn_Compare(cls, ctx, e):
        left = e.left
        try:
            ctx.ana(left, ieee_ty)
        except TyError:
            ctx.ana(left, num_ty)
        for op, comparator in zip(e.ops, e.comparators):
            if isinstance(op, (ast.In, ast.NotIn)):
                raise TyError(
                    "Invalid comparison operator for num.", 
                    comparator)
            try:
                ctx.ana(comparator, ieee_ty)
            except TyError:
                ctx.ana(comparator, num_ty)
        return boolean_ty

    @classmethod
    def trans_Compare(cls, ctx, e):
        return ast.copy_location(
            ast.Compare(
                left=ctx.trans(e.left),
                ops=e.ops,
                comparators=[
                    ctx.trans(comparator)
                    for comparator in e.comparators]), e)
    
ieee_ty = CanonicalTy(ieee, ())

class cplx(Fragment):
    # TODO init_idx
    # TODO intro_forms
    # TODO other operations
    # TODO pattern matching
    pass

def _update_name_bindings_disjoint(bindings, new_bindings):
    for name_ast, ty in new_bindings.items():
        for name_ast_orig, _ in bindings.items():
            if name_ast.id == name_ast_orig.id:
                raise TyError("Duplicated binding.", name_ast)
        bindings[name_ast] = ty

class record(Fragment):
    @classmethod
    def init_idx(cls, ctx, idx_ast):
        if isinstance(idx_ast, ast.Slice):
            # Python special cases single slices
            # we don't want that
            idx_ast = ast.ExtSlice(dims=[idx_ast])
        
        if isinstance(idx_ast, ast.ExtSlice):
            idx_value = dict() # returned below
            for dim in idx_ast.dims:
                if (isinstance(dim, ast.Slice) and 
                        dim.step is None and
                        dim.upper is not None and 
                        isinstance(dim.lower, ast.Name)):
                    lbl = dim.lower.id
                    if lbl in idx_value:
                        raise TypeValidationError(
                            "Duplicate label.", dim)
                    ty = ctx.as_type(dim.upper)
                    idx_value[lbl] = ty
                else:
                    raise TypeValidationError(
                        "Invalid field specification.", dim)
            return idx_value
        else:
            raise TypeValidationError(
                "Invalid record specification.", idx_ast)

    @classmethod
    def ana_Dict(cls, ctx, e, idx):
        for lbl, value in zip(e.keys, e.values):
            if isinstance(lbl, ast.Name):
                id = lbl.id
                if id in idx: ctx.ana(value, idx[id])
                else:
                    raise TyError("Invalid label: " + id, lbl)
            else:
                raise TyError("Label is not an identifier.", lbl)
        
        if len(idx) != len(e.keys):
            raise TyError("Labels do not match those in type.", e)

    @classmethod
    def trans_Dict(cls, ctx, e, idx):
        ast_dict = dict((k.id, v)
                        for k, v in zip(e.keys, e.values))
        return ast.copy_location(ast.Tuple(
            elts=list(
                ctx.trans(ast_dict[lbl])
                for lbl in sorted(idx.keys())
            ), ctx=ast.Load()), 
            e)

    @classmethod
    def ana_pat_Dict(cls, ctx, pat, idx):
        keys, values = pat.keys, pat.values
        n_keys = len(pat.keys)
        n_fields = len(idx)
        if n_keys < n_fields:
            raise TyError("Missing fields.", pat)
        elif n_keys > n_fields:
            raise TyError("Too many fields.", pat)
        else:
            bindings = { }
            for key, value in zip(keys, values):
                if isinstance(key, ast.Name):
                    key_id = key.id
                    try:
                        ty = idx[key_id]
                    except KeyError:
                        raise TyError("Invalid field name: " + key_id, key)
                    else:
                        new_bindings = ctx.ana_pat(value, ty)
                        _update_name_bindings_disjoint(bindings, new_bindings)
                else:
                    raise TyError("Invalid record field.", key)
            return bindings

    @classmethod
    def trans_pat_Dict(cls, ctx, pat, idx, scrutinee_trans):
        keys, values = pat.keys, pat.values
        sorted_idx = sorted(idx.keys())
        conditions = []
        binding_translations = { }
        for key, value in zip(keys, values):
            key_id = key.id
            key_scrutinee = ast.fix_missing_locations(ast.copy_location(
                ast.Subscript(
                    value=scrutinee_trans,
                    slice=ast.Index(
                        value=ast.Num(n=_util._seq_pos_of(key_id, sorted_idx))),
                    ctx=astx.load_ctx),
                key))
            condition, key_binding_translations = ctx.trans_pat(value, key_scrutinee) 
            conditions.append(condition)
            binding_translations.update(key_binding_translations)
        condition = ast.fix_missing_locations(ast.copy_location(
            ast.BoolOp(
                op=ast.And(),
                values=conditions),
            pat))
        return condition, binding_translations

    @classmethod
    def ana_pat_Set(cls, ctx, pat, idx):
        elts = pat.elts
        n_elts = len(elts)
        n_fields = len(idx)
        if n_elts < n_fields:
            raise TyError("Missing fields.", pat)
        elif n_elts > n_fields:
            raise TyError("Too many fields.", pat)
        else:
            bindings = { }
            for elt in elts:
                if isinstance(elt, ast.Name):
                    id = elt.id
                    try:
                        ty = idx[id]
                    except KeyError:
                        raise TyError("Invalid field name: " + id, elt)
                    else:
                        new_bindings = ctx.ana_pat(elt, ty)
                        _update_name_bindings_disjoint(bindings, new_bindings)
                else:
                    raise TyError("Invalid record field.", elt)
            return bindings

    @classmethod
    def trans_pat_Set(cls, ctx, pat, idx, scrutinee_trans):
        elts = pat.elts
        sorted_idx = sorted(idx.keys())
        binding_translations = { }
        for elt in elts:
            key_id = elt.id
            key_scrutinee = ast.fix_missing_locations(ast.copy_location(
                ast.Subscript(
                    value=scrutinee_trans,
                    slice=ast.Index(
                        value=ast.Num(n=_util._seq_pos_of(key_id, sorted_idx))),
                    ctx=astx.load_ctx),
                elt))
            _, key_binding_translations = ctx.trans_pat(elt, key_scrutinee) 
            binding_translations.update(key_binding_translations)
        condition = ast.copy_location(
            ast.NameConstant(True),
            pat)
        return condition, binding_translations

    @classmethod
    def syn_Attribute(cls, ctx, e, idx):
        try:
            return idx[e.attr]
        except KeyError:
            raise TyError("Invalid field label: " + e.attr, e)

    @classmethod
    def trans_Attribute(cls, ctx, e, idx):
        pos = _util._seq_pos_of(e.attr, sorted(idx.keys()))
        return ast.fix_missing_locations(ast.copy_location(
            ast.Subscript(
                value=ctx.trans(e.value),
                slice=ast.Index(ast.Num(n=pos)),
                ctx=e.ctx),
            e))

class tpl(Fragment):
    @classmethod
    def init_idx(cls, ctx, idx_ast):
        if isinstance(idx_ast, ast.Slice):
            # special case for a single
            idx_ast = ast.ExtSlice(dims=[idx_ast])
        elif isinstance(idx_ast, ast.Index):
            value = idx_ast.value
            if isinstance(value, ast.Tuple):
                idx_ast = ast.ExtSlice(
                    dims=[ast.Index(value=elt)
                          for elt in value.elts])
            else:
                idx_ast = ast.ExtSlice(dims=[idx_ast])
        
        if isinstance(idx_ast, ast.ExtSlice):
            idx_value = OrderedDict()
            for n, dim in enumerate(idx_ast.dims):
                if isinstance(dim, ast.Index):
                    lbl = n
                    ty_ast = dim.value
                elif (isinstance(dim, ast.Slice)
                      and dim.step is None
                      and dim.upper is not None and 
                      isinstance(dim.lower, ast.Name)):
                    lbl = dim.lower.id
                    ty_ast = dim.upper
                else:
                    raise TypeValidationError(
                        "Invalid tpl specification.", idx_ast)
                if lbl in idx_value:
                    raise TypeValidationError(
                        "Duplicate label.", dim)
                ty = ctx.as_type(ty_ast)
                idx_value[lbl] = ty
            return idx_value
        else:
            raise TypeValidationError(
                "Invalid tpl specification.", idx_ast)

    @classmethod
    def ana_Tuple(cls, ctx, e, idx):
        elts = e.elts
        for elt, ty in zip(elts, idx.values()):
            ctx.ana(elt, ty)

        if len(elts) != len(idx):
            raise TyError("Incorrect nunmber of elements.", e)

    @classmethod
    def trans_Tuple(cls, ctx, e, idx):
        return ast.copy_location(
            ast.Tuple(
                elts=[ctx.trans(elt) for elt in e.elts],
                ctx=e.ctx),
            e)

    @classmethod
    def _get_key(cls, lbl):
        if isinstance(lbl, ast.Name):
            key = lbl.id
        elif isinstance(lbl, ast.Num):
            key = lbl.n
        else:
            raise TyError("Invalid label.", lbl)
        return key

    @classmethod
    def ana_Dict(cls, ctx, e, idx):
        for lbl, value in zip(e.keys, e.values):
            key = cls._get_key(lbl)
            try:
                ty = idx[key]
            except KeyError:
                raise TyError("Label not found in type.", lbl)
            else:
                ctx.ana(value, ty)

        if len(idx) != len(e.keys):
            raise TyError("Labels do not match those in type.", e)

    @classmethod
    def trans_Dict(cls, ctx, e, idx):
        # TODO order of evaluation?
        ast_dict = dict((cls._get_key(k), v)
                        for k, v in zip(e.keys, e.values))
        return ast.copy_location(
            ast.Tuple(
                elts=[
                    ctx.trans(ast_dict[key])
                    for key in idx.keys()],
                ctx=astx.load_ctx),
            e)

    @classmethod
    def ana_pat_Tuple(cls, ctx, pat, idx):
        elts = pat.elts
        bindings = { }
        for elt, ty in zip(elts, idx.values()):
            new_bindings = ctx.ana_pat(elt, ty)
            _update_name_bindings_disjoint(bindings, new_bindings)
        
        if len(elts) != len(idx):
            raise TyError("Incorrect number of elements.", pat)

        return bindings

    @classmethod
    def trans_pat_Tuple(cls, ctx, pat, idx, scrutinee_trans):
        conditions = []
        binding_translations = { }
        for i, elt in enumerate(pat.elts):
            elt_scrutinee = ast.fix_missing_locations(ast.copy_location(
                ast.Subscript(
                    value=scrutinee_trans,
                    slice=ast.Index(value=ast.Num(n=i)),
                    ctx=astx.load_ctx),
                elt))
            condition, elt_binding_translations = \
                ctx.trans_pat(elt, elt_scrutinee)
            conditions.append(condition)
            binding_translations.update(elt_binding_translations)
        condition = ast.fix_missing_locations(ast.copy_location(
            ast.BoolOp(
                op=ast.And(),
                values=conditions),
            pat))
        return condition, binding_translations

    @classmethod
    def ana_pat_Dict(cls, ctx, pat, idx):
        keys, values = pat.keys, pat.values
        n_keys = len(pat.keys)
        n_fields = len(idx)
        if n_keys < n_fields:
            raise TyError("Missing fields.", pat)
        elif n_keys > n_fields:
            raise TyError("Too many fields.", pat)
        else:
            bindings = { }
            for key, value in zip(keys, values):
                k = cls._get_key(key)
                try:
                    ty = idx[k]
                except KeyError:
                    raise TyError("Field not found.", key)
                else:
                    new_bindings = ctx.ana_pat(value, ty)
                    _update_name_bindings_disjoint(bindings, new_bindings)
            return bindings

    @classmethod
    def trans_pat_Dict(cls, ctx, pat, idx, scrutinee_trans):
        keys, values = pat.keys, pat.values
        conditions = []
        binding_translations = { }
        idx_lbls = list(idx.keys())
        for key, value in zip(keys, values):
            k = cls._get_key(key)
            key_scrutinee = ast.fix_missing_locations(ast.copy_location(
                ast.Subscript(
                    value=scrutinee_trans,
                    slice=ast.Index(
                        value=ast.Num(n=_util._seq_pos_of(k, idx_lbls))), 
                    ctx=astx.load_ctx), 
                key))
            condition, key_binding_translations = \
                ctx.trans_pat(value, key_scrutinee)
            conditions.append(condition)
            binding_translations.update(key_binding_translations)
        condition = ast.fix_missing_locations(ast.copy_location(
            ast.BoolOp(
                op=ast.And(),
                values=conditions),
            pat))
        return condition, binding_translations

    @classmethod
    def ana_pat_Set(cls, ctx, pat, idx):
        elts = pat.elts
        n_elts = len(elts)
        n_fields = len(idx)
        if n_elts < n_fields:
            raise TyError("Missing fields.", pat)
        elif n_elts > n_fields:
            raise TyError("Too many fields.", pat)
        else:
            bindings = { }
            for elt in elts:
                if isinstance(elt, ast.Name):
                    id = elt.id
                    try:
                        ty = idx[id]
                    except KeyError:
                        raise TyError("Invalid field name: " + id, elt)
                    else:
                        new_bindings = ctx.ana_pat(elt, ty)
                        _update_name_bindings_disjoint(bindings, new_bindings)
                else:
                    raise TyError("Invalid record field.", elt)
            return bindings

    @classmethod
    def trans_pat_Set(cls, ctx, pat, idx, scrutinee_trans):
        elts = pat.elts
        idx_keys = list(idx.keys())
        binding_translations = { }
        for elt in elts:
            key_id = elt.id
            key_scrutinee = ast.fix_missing_locations(ast.copy_location(
                ast.Subscript(
                    value=scrutinee_trans,
                    slice=ast.Index(
                        value=ast.Num(n=_util._seq_pos_of(key_id, idx_keys))),
                    ctx=astx.load_ctx),
                elt))
            _, key_binding_translations = ctx.trans_pat(elt, key_scrutinee)
            binding_translations.update(key_binding_translations)
        condition = ast.copy_location(
            ast.NameConstant(True),
            pat)
        return condition, binding_translations

    @classmethod
    def syn_Attribute(cls, ctx, e, idx):
        try:
            return idx[e.attr]
        except KeyError:
            raise TyError("Invalid field label: " + e.attr, e)

    @classmethod
    def trans_Attribute(cls, ctx, e, idx):
        pos = _util._seq_pos_of(e.attr, idx.keys())
        return ast.fix_missing_locations(ast.copy_location(
            ast.Subscript(
                value=ctx.trans(e.value),
                slice=ast.Index(ast.Num(n=pos)),
                ctx=e.ctx),
            e))

    @classmethod
    def syn_Subscript(cls, ctx, e, idx):
        slice = e.slice
        if isinstance(slice, ast.Index):
            value = slice.value
            if isinstance(value, ast.Num):
                try:
                    return idx[value.n]
                except KeyError:
                    raise TyError("Invalid field position.", value)
            else:
                raise TyError("Invalid field position.", value)
        else:
            raise TyError("Invalid subscript.", e)

    @classmethod
    def trans_Subscript(cls, ctx, e, idx):
        n = e.slice.value.n
        pos = _util._seq_pos_of(n, idx.keys())
        return ast.fix_missing_locations(ast.copy_location(
            ast.Subscript(
                value=ctx.trans(e.value),
                slice=ast.Index(ast.Num(n=pos)),
                ctx=e.ctx),
            e))

class variant(Fragment):
    @classmethod
    def init_idx(cls, ctx, idx_ast):
        if isinstance(idx_ast, ast.Index):
            value = idx_ast.value
            if not isinstance(value, ast.Tuple):
                value = ast.Tuple(elts=[value], ctx=astx.load_ctx)
            idx = { } 
            for elt in value.elts:
                if isinstance(elt, ast.Name):
                    tag = elt.id
                    tag_ast = elt
                    ty_asts = []
                elif (isinstance(elt, ast.Call)  
                      and isinstance(elt.func, ast.Name)
                      and len(elt.keywords) == 0):
                    tag = elt.func.id
                    tag_ast = elt.func
                    ty_asts = elt.args
                else:
                    raise TypeValidationError(
                        "Invalid case specification.", elt)
                if not tag[0].isupper():
                    raise TypeValidationError(
                        "Tag must start with an uppercase letter.", tag_ast)
                if tag in idx:
                    raise TypeValidationError(
                        "Duplicate tag: " + tag, tag_ast)
                types = tuple(
                    ctx.as_type(ty_ast) 
                    for ty_ast in ty_asts)
                idx[tag] = types
            return idx
        else:
            raise TypeValidationError(
                "Invalid case specification.", elt)

    @classmethod
    def ana_Name(cls, ctx, e, idx):
        tag = e.id
        try: types = idx[tag]
        except: raise TyError("Invalid tag: " + tag, e)
        if len(types) != 0:
            raise TyError(
                "Missing arguments to constructor.", e)

    @classmethod
    def trans_Name(cls, ctx, e, idx):
        return ast.fix_missing_locations(ast.copy_location(
            ast.Tuple(
                elts=[ast.Str(s=e.id)],
                ctx=astx.load_ctx),
            e))

    @classmethod
    def ana_Call(cls, ctx, e, idx):
        func, args, keywords = e.func, e.args, e.keywords
        if len(keywords) != 0:
            raise TyError("Keyword arguments are not supported.", e)
        if isinstance(func, ast.Name):
            tag = func.id
            try: types = idx[tag]
            except: raise TyError("Invalid tag: " + tag, func)
            n_types = len(types)
            n_args = len(args)
            if n_args > n_types:
                raise TyError("Too many arguments.", e)
            elif n_args < n_types:
                raise TyError("Too few arguments.", e) 
            else:
                for arg, ty in zip(args, types):
                    ctx.ana(arg, ty)
        else:
            raise TyError("Invalid tag.", func)

    @classmethod
    def trans_Call(cls, ctx, e, idx=None):
        elts = [ast.copy_location(ast.Str(s=e.func.id), e)]
        args = e.args
        elts.extend([
            ctx.trans(arg)
            for arg in args])
        return ast.copy_location(
            ast.Tuple(
                elts=elts,
                ctx=astx.load_ctx), 
            e)

    @classmethod
    def ana_pat_Name(cls, ctx, pat, idx):
        tag = pat.id
        try: types = idx[tag]
        except: raise TyError("Invalid tag.", pat)
        if len(types) != 0:
            raise TyError("Missing arguments to constructor.", pat)
        return { }

    @classmethod
    def trans_pat_Name(cls, ctx, pat, idx, scrutinee_trans):
        condition = ast.fix_missing_locations(ast.copy_location(
            ast.Compare(
                left=ast.Subscript(
                    value=scrutinee_trans,
                    slice=ast.Index(value=ast.Num(n=0)),
                    ctx=astx.load_ctx),
                ops=[ast.Eq()],
                comparators=[ast.Str(s=pat.id)]),
            pat))
        return condition, { }

    @classmethod
    def ana_pat_Call(cls, ctx, pat, idx):
        func, args, keywords = pat.func, pat.args, pat.keywords
        if len(keywords) != 0:
            raise TyError("Keyword arguments are not supported.", pat)
        if isinstance(func, ast.Name):
            tag = func.id
            try: types = idx[tag]
            except: raise TyError("Invalid tag: " + tag, pat)
            n_types = len(types)
            n_args = len(args)
            if n_args > n_types:
                raise TyError("Too many arguments.", pat)
            elif n_args < n_types:
                raise TyError("Too few arguments.", pat)
            else:
                bindings = { }
                for arg, ty in zip(args, types):
                    arg_bindings = ctx.ana_pat(arg, ty)
                    _update_name_bindings_disjoint(bindings, arg_bindings)
                return bindings
        else:
            raise TyError("Invalid tag.", func)

    @classmethod
    def trans_pat_Call(cls, ctx, pat, idx, scrutinee_trans):
        tag = pat.func.id
        tag_condition = ast.fix_missing_locations(ast.copy_location(
            ast.Compare(
                left=ast.Subscript(
                    value=scrutinee_trans,
                    slice=ast.Index(value=ast.Num(n=0)),
                    ctx=astx.load_ctx),
                ops=[ast.Eq()],
                comparators=[ast.Str(s=tag)]), 
            pat))
        conditions = [tag_condition]
        binding_translations = { }
        for i, arg in enumerate(pat.args):
            arg_scrutinee = ast.copy_location(
                ast.Subscript(
                    value=scrutinee_trans,
                    slice=ast.fix_missing_locations(ast.copy_location(
                        ast.Index(value=ast.Num(n=1 + i)), 
                        pat)),
                    ctx=astx.load_ctx), 
                pat)
            arg_condition, arg_binding_translations = ctx.trans_pat(arg, arg_scrutinee)
            conditions.append(arg_condition)
            binding_translations.update(arg_binding_translations)
        condition = ast.copy_location(
            ast.BoolOp(
                op=ast.copy_location(ast.And(), pat), 
                values=conditions), 
            pat)
        return condition, binding_translations

class fn(Fragment):
    @classmethod
    def init_idx(cls, ctx, idx_ast):
        if isinstance(idx_ast, ast.Index):
            value = idx_ast.value
            if isinstance(value, ast.Compare):
                left, ops, comparators = value.left, value.ops, value.comparators
                if len(ops) == len(comparators) == 1:
                    if isinstance(ops[0], ast.Gt):
                        if isinstance(left, ast.Tuple):
                            if len(left.elts) == 0:
                                arg_type_asts = []
                            else:
                                raise TypeValidationError(
                                    "Invalid type index format.", idx_ast)
                        else:
                            arg_type_asts = [left]
                        return_ty_ast = comparators[0]
                    else:
                        raise TypeValidationError(
                            "Invalid type index format.", idx_ast)
                else:
                    raise TypeValidationError(
                        "Invalid type index format.", idx_ast)
            elif isinstance(value, ast.Tuple):
                elts = value.elts
                if len(elts) < 2:
                    raise TypeValidationError(
                        "Invalid type index format.", idx_ast)
                arg_type_asts = elts[0:-1]
                final_elt = elts[-1]
                if isinstance(final_elt, ast.Compare):
                    left, ops, comparators = \
                        final_elt.left, final_elt.ops, final_elt.comparators
                    if len(ops) == len(comparators) == 1:
                        if isinstance(ops[0], ast.Gt):
                            arg_type_asts.append(left)
                            return_ty_ast = comparators[0]
                        else:
                            raise TypeValidationError(
                                "Invalid type index format.", idx_ast)
                    else:
                        raise TypeValidationError(
                            "Invalid type index format.", idx_ast)
                else:
                    raise TypeValidationError(
                        "Invalid type index format.", idx_ast)
            else:
                raise TypeValidationError(
                    "Invalid type index format.", idx_ast)
            arg_types = tuple(
                ctx.as_type(arg_ty)
                for arg_ty in arg_type_asts)
            return_ty = ctx.as_type(return_ty_ast)
            return (arg_types, return_ty)
        else:
            raise typy.TypeValidationError(
                "Invalid type index format.", idx_ast)

    @classmethod
    def syn_FunctionDef(cls, ctx, stmt):
        # process decorators
        decorator_list = stmt.decorator_list
        if len(decorator_list) > 1:
            raise TyError(
                "fn does not support additional decorators.",
                decorator_list[1])

        # process args
        arguments = stmt.args
        if arguments.vararg is not None:
            raise TyError(
                "fn does not support varargs", arguments)
        if len(arguments.kwonlyargs) > 0:
            raise TyError(
                "fn does not support kw only args", arguments)
        if arguments.kwarg is not None:
            raise TyError(
                "fn does not support kw arg", arguments)
        if len(arguments.defaults) > 0:
            raise TyError(
                "fn does not support defaults", arguments)
        args = arguments.args
        def _process_args():
            for arg in args:
                arg_id = arg.arg
                arg_ann = arg.annotation
                if arg_ann is None:
                    raise TyError(
                        "Missing argument type on " + arg_id,
                        arg)
                arg_ty = ctx.as_type(arg_ann)
                # simulate a name for the error reporting system
                name = ast.Name(id=arg_id, 
                                lineno=arg.lineno, 
                                col_offset=arg.col_offset)
                yield (name, arg_ty)
        arg_sig = stmt.arg_sig = OrderedDict(_process_args())
        arg_types = tuple(arg_sig.values())

        # process return type annotation
        returns = stmt.returns
        if returns is not None:
            rty = ctx.as_type(returns)
        else: 
            rty = None
        
        # push bindings
        if rty is not None:
            self_name = ast.copy_location(
                ast.Name(id=stmt.name),
                stmt)
            self_ty = CanonicalTy(cls, (arg_types, rty))
            ctx.push_var_bindings({self_name : self_ty})  
        stmt.uniq_arg_sig = ctx.push_var_bindings(dict(arg_sig))

        # process docstring
        body = stmt.body
        if (len(body) > 1
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Str)):
            proper_body = stmt.proper_body = body[1:]
            docstring = stmt.docstring = body[0].value.s
        else:
            proper_body = stmt.proper_body = body
            docstring = stmt.docstring = None

        # make sure there is at least one remaining statement
        if len(proper_body) == 0:
            raise TyError(
                "Must be at least one statement, "
                "other than the docstring, in the body.",
                stmt)

        # check statements in proper_body
        proper_body_block = stmt.proper_body_block = _terms.Block(proper_body)
        if rty is None:
            rty = ctx.syn_block(proper_body_block)
        else:
            ctx.ana_block(proper_body_block, rty)

        # return canonical type
        return CanonicalTy(fn, (arg_types, rty))

    @classmethod
    def ana_FunctionDef(cls, ctx, stmt, idx):
        # process decorators
        decorator_list = stmt.decorator_list
        if len(decorator_list) == 1:
            asc = decorator_list[0]
            try: ty = ctx.as_type(asc)
            except:
                try: fragment = ctx.static_env.eval_expr_ast(asc)
                except: 
                    raise TyError(
                        "Decorator is neither a type nor a fragment.", stmt)
                else:
                    if fragment != cls:
                        raise TyError("Decorator is not fn.", stmt)
            else:
                canonical_ty = ctx.canonicalize(ty)
                asc_idx = canonical_ty.idx
                if idx != asc_idx:
                    raise TyError("Decorator is inconsistent with expected type.", stmt)
                
        if len(decorator_list) > 1:
            raise TyError(
                "fn does not support decorators in analytic position.",
                decorator_list[1])

        # process args
        arguments = stmt.args
        if arguments.vararg is not None:
            raise TyError(
                "fn does not support varargs", arguments)
        if len(arguments.kwonlyargs) > 0:
            raise TyError(
                "fn does not support kw only args", arguments)
        if arguments.kwarg is not None:
            raise TyError(
                "fn does not support kw arg", arguments)
        if len(arguments.defaults) > 0:
            raise TyError(
                "fn does not support defaults", arguments)
        args = arguments.args
        arg_types = idx[0]
        n_args = len(args)
        n_arg_types = len(arg_types)
        if n_args < n_arg_types:
            raise TyError(
                "Too few arguments", stmt)
        elif n_args > n_arg_types:
            raise TyError(
                "Too many arguments", stmt)
        def _process_args():
            for arg, arg_ty in zip(args, arg_types):
                arg_id = arg.arg
                arg_ann = arg.annotation 
                if arg_ann is not None:
                    given_arg_ty = ctx.as_type(arg_ann)
                    if not ctx.ty_expr_eq(arg_ty, given_arg_ty, TypeKind):
                        raise TyError(
                            "Given type annotation is inconsistent "
                            "with ascription.", arg_ann)
                name = ast.Name(id=arg_id,
                                lineno=arg.lineno,
                                col_offset=arg.col_offset)
                yield (name, arg_ty)
        arg_sig = stmt.arg_sig = OrderedDict(_process_args())

        returns = stmt.returns
        rty = idx[1]
        if returns is not None: 
            ann_rty = ctx.as_type(returns)
            if not ctx.ty_expr_eq(rty, ann_rty, TypeKind):
                raise TyError(
                    "Given return type annotation is inconsistent "
                    "with ascription.", returns)

        # push bindings
        self_name = ast.copy_location(
            ast.Name(id=stmt.name),
            stmt)
        self_ty = CanonicalTy(cls, (arg_types, rty))
        ctx.push_var_bindings({self_name : self_ty})  
        stmt.uniq_arg_sig = ctx.push_var_bindings(dict(arg_sig))

        # process docstring
        body = stmt.body
        if (len(body) > 1 
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Str)):
            proper_body = stmt.proper_body = body[1:]
            docstring = stmt.docstring = body[0].value.s
        else:
            proper_body = stmt.proper_body = body
            docstring = stmt.docstring = None

        # make sure there is at least one remaining statement
        if len(proper_body) == 0:
            raise TyError(
                "Must be at least one statement, "
                "other than the docstring, in the body.",
                stmt)

        # check statements in proper_body
        proper_body_block = stmt.proper_body_block = _terms.Block(proper_body)
        ctx.ana_block(proper_body_block, rty)

        # bindings
        ctx.pop_var_bindings()

    @classmethod
    def trans_FunctionDef(cls, ctx, stmt, idx, mechanism):
        uniq_id = stmt.uniq_id

        # translate arguments
        arguments_tr = ast.arguments(
            args= [
                ast.arg(
                    arg=stmt.uniq_arg_sig[arg.arg][0],
                    annotation=None,
                    lineno=arg.lineno,
                    col_offset=arg.col_offset)
                for arg in stmt.args.args
            ],
            vararg=None,
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None,
            defaults=[])

        # translate body
        body_tr = ctx.trans_block(stmt.proper_body_block, 
                                  BlockTransMechanism.Return)

        return [ast.copy_location(
            ast.FunctionDef(
                name=uniq_id,
                args=arguments_tr,
                body=body_tr,
                decorator_list=[],
                returns=None), 
            stmt)]

    @classmethod
    def ana_Lambda(cls, ctx, e, idx):
        # process args
        arguments = e.args
        if arguments.vararg is not None:
            raise TyError(
                "fn does not support varargs", arguments)
        if len(arguments.kwonlyargs) > 0:
            raise TyError(
                "fn does not support kw only args", arguments)
        if arguments.kwarg is not None:
            raise TyError(
                "fn does not support kw arg", arguments)
        if len(arguments.defaults) > 0:
            raise TyError(
                "fn does not support defaults", arguments)
        args = arguments.args
        arg_types = idx[0]
        n_args = len(args)
        n_arg_types = len(arg_types)
        if n_args < n_arg_types:
            raise TyError(
                "Too few arguments", e)
        elif n_args > n_arg_types:
            raise TyError(
                "Too many arguments", e)
        def _process_args():
            for arg, arg_ty in zip(args, arg_types):
                arg_id = arg.arg
                name = ast.Name(id=arg_id,
                                lineno=arg.lineno,
                                col_offset=arg.col_offset)
                yield (name, arg_ty)
        arg_sig = e.arg_sig = OrderedDict(_process_args())
        e.uniq_arg_sig = ctx.push_var_bindings(dict(arg_sig))

        rty = idx[1]
        ctx.ana(e.body, rty)
        
        ctx.pop_var_bindings()

    @classmethod
    def trans_Lambda(cls, ctx, e, idx):
        args=e.args
        aa = args.args
        return ast.copy_location(
            ast.Lambda(
                args=ast.arguments(
                    args=[
                        ast.arg(
                            arg=a.arg,
                            annotation=None,
                            lineno=a.lineno,
                            col_offset=a.col_offset)
                        for a in aa
                    ],
                    vararg=args.vararg,
                    kwonlyargs=args.kwonlyargs,
                    kw_defaults=args.kw_defaults,
                    kwarg=args.kwarg,
                    defaults=args.defaults),
                body=ctx.trans(e.body)),
            e)

    @classmethod
    def syn_Call(cls, ctx, e, idx):
        if len(e.keywords) != 0:
            raise TyError("fn does not support keyword arguments.", e)

        # check args
        args = e.args
        arg_types, rty = idx
        n_args = len(args)
        n_args_reqd = len(arg_types)
        if n_args < n_args_reqd:
            raise TyError("Too few arguments provided.", e)
        elif n_args > n_args_reqd:
            raise TyError("Too many arguments provided.", e)
        for arg, arg_ty in zip(args, arg_types):
            ctx.ana(arg, arg_ty)
        
        # return type
        return rty

    @classmethod
    def trans_Call(cls, ctx, e, idx):
        return ast.copy_location(
            ast.Call(
                func=ctx.trans(e.func),
                args=[
                    ctx.trans(arg)
                    for arg in e.args],
                keywords=[]),
            e)

    @classmethod
    def check_Assign(cls, ctx, stmt):
        targets = stmt.targets
        if len(targets) != 1:
            # TODO support for multiple targets
            raise TyError(
                "Too many assignment targets.", targets[1])
        target = targets[0]
        pat, ann = _terms.get_pat_and_ann(target)
        if ann is not None:
            ty = ctx.as_type(ann)
            ctx.ana(stmt.value, ty)
        else:
            ty = ctx.syn(stmt.value)
        bindings = stmt.bindings = ctx.ana_pat(pat, ty)
        stmt.uniq_bindings = ctx.add_bindings(bindings)
    
    @classmethod
    def trans_checked_Assign(cls, ctx, stmt):
        target_name = tuple(stmt.bindings.keys())[0]
        target_tr = ast.copy_location(
            ast.Name(id=stmt.uniq_bindings[target_name.id][0],
                     ctx=astx.store_ctx),
            target_name)
        value = stmt.value
        value_tr = ast.copy_location(
            ctx.trans(value),
            value)
        return [ast.copy_location(
            ast.Assign(
                targets=[target_tr],
                value=value_tr),
            stmt)]

    @classmethod
    def integrate_static_FunctionDef(cls, ctx, stmt):
        name_ast = ast.copy_location(
            ast.Name(id=stmt.name, ctx=astx.load_ctx),
            stmt)
        stmt.uniq_bindings = uniq_bindings = ctx.add_bindings({ name_ast: stmt.ty })
        stmt.uniq_id = uniq_bindings[stmt.name][0]

    @classmethod
    def integrate_trans_FunctionDef(cls, ctx, stmt, translation, mechanism):
        uniq_id = stmt.uniq_id
        if mechanism == BlockTransMechanism.Return:
            translation.append(ast.copy_location(
                ast.Return(
                    value=ast.copy_location(
                        ast.Name(
                            id=uniq_id,
                            ctx=astx.load_ctx),
                        stmt)),
                stmt))

class py(Fragment):
    @classmethod
    def init_idx(cls, ctx, idx_ast):
        return _check_trivial_idx_ast(idx_ast)

    @classmethod
    def check_Assign(cls, ctx, stmt, idx):
        target = stmt.targets[0]
        if isinstance(target, ast.Subscript):
            cls._ana_slice(ctx, target.slice)
        ctx.ana(stmt.value, py_type)

    @classmethod
    def check_AugAssign(cls, ctx, stmt, idx):
        target = stmt.target
        if isinstance(target, ast.Subscript):
            cls._ana_slice(ctx, target.slice)
        ctx.ana(stmt.value, py_type)

    @classmethod
    def syn_Assign(cls, ctx, stmt, idx):
        cls.check_Assign(ctx, stmt, idx)
        return py_type

    @classmethod
    def syn_AugAssign(cls, ctx, stmt, idx):
        cls.check_AugAssign(ctx, stmt, idx)
        return py_type

    @classmethod
    def trans_Assign(cls, ctx, stmt, idx, 
                     mechanism=BlockTransMechanism.Statement):
        return cls._trans_Assign_AugAssign(ctx, stmt, idx, mechanism)

    @classmethod
    def trans_AugAssign(cls, ctx, stmt, idx,
                        mechanism=BlockTransMechanism.Statement):
        return cls._trans_Assign_AugAssign(ctx, stmt, idx, mechanism)

    @classmethod
    def _trans_Assign_AugAssign(cls, ctx, stmt, idx, mechanism): 
        if isinstance(stmt, ast.Assign):
            target = stmt.targets[0]
        else:
            target = stmt.target
        if isinstance(target, ast.Attribute):
            # target_translation = ast.copy_location(
            #     ast.Name(id="ABCABDBDASD", ctx=astx.store_ctx), target)
            target_translation = ast.copy_location(
                ast.Attribute(
                    value=ctx.trans(target.value),
                    attr=target.attr,
                    ctx=target.ctx),
                stmt)
        else:
            target_translation = ast.copy_location(
                ast.Subscript(
                    value=ctx.trans(target.value),
                    slice=cls._trans_slice(ctx, target.slice),
                    ctx=target.ctx),
                target)
        if isinstance(stmt, ast.Assign):
            assign_translation = ast.copy_location(
                ast.Assign(
                    targets=[target_translation],
                    value=ctx.trans(stmt.value)),
                stmt)
        else:
            assign_translation = ast.copy_location(
                ast.AugAssign(
                    target=target_translation,
                    op=stmt.op,
                    value=ctx.trans(stmt.value)), 
                stmt)
        if mechanism == BlockTransMechanism.Statement:
            statement = [assign_translation]
        elif mechanism == BlockTransMechanism.Returns:
            return_translation = ast.copy_location(
                ast.Return(value=None), stmt)
            statement = [assign_translation, return_translation] 
        else: raise Exception("Unexpected mechanism.")
        return statement

    @classmethod
    def syn_If(cls, ctx, stmt, idx):
        body_block = stmt.body_block = _terms.Block(stmt.body)
        body_ty = ctx.syn_block(body_block)
        orelse = stmt.orelse
        if len(orelse) > 0:
            orelse_block = stmt.orelse_block = _terms.Block(orelse)
            ctx.ana_block(orelse_block, body_ty)
        return body_ty

    @classmethod
    def ana_If(cls, ctx, stmt, idx, ty):
        body_block = stmt.body_block = _terms.Block(stmt.body)
        ctx.ana_block(body_block, ty)
        orelse = stmt.orelse
        if len(orelse) > 0:
            orelse_block = stmt.orelse_block = _terms.Block(stmt.orelse)
            ctx.ana_block(orelse_block, ty)

    @classmethod
    def trans_If(cls, ctx, stmt, id, mechanism):
        orelse = stmt.orelse
        if len(orelse) > 0:
            orelse_translation = ctx.trans_block(stmt.orelse_block, mechanism)
        else:
            orelse_translation=[]
        return [ast.fix_missing_locations(ast.copy_location(
            ast.If(
                test=ctx.trans(stmt.test),
                body=ctx.trans_block(stmt.body_block, mechanism),
                orelse=orelse_translation),
            stmt))]

    @classmethod
    def ana_Num(cls, ctx, e, idx):
        return

    @classmethod
    def trans_Num(cls, ctx, e, idx):
        return ast.copy_location(
            ast.Num(n=e.n),
            e)

    @classmethod
    def ana_pat_Num(cls, ctx, pat, idx):
        return {}

    @classmethod
    def trans_pat_Num(cls, ctx, pat, idx, scrutinee_tr):
        condition = ast.copy_location(
            ast.Compare(
                left=scrutinee_tr,
                ops=[ast.Eq()],
                comparators=[ast.copy_location(
                    ast.Num(n=pat.n),
                    pat)]),
            pat)
        return condition, {}

    @classmethod
    def ana_UnaryOp(cls, ctx, e, idx):
        ctx.ana(e.operand, py_type)

    @classmethod
    def trans_UnaryOp(cls, ctx, e, idx=None):
        return ast.copy_location(
            ast.UnaryOp(
                op=e.op,
                operand=ctx.trans(e.operand)),
            e)

    @classmethod
    def ana_pat_UnaryOp(cls, ctx, pat, idx):
        op, operand = pat.op, pat.operand
        if isinstance(op, (ast.USub, ast.UAdd)):
            if isinstance(operand, ast.Num):
                return {}
            else:
                raise TyError("Invalid operand pattern.", operand)
        elif isinstance(op, ast.Not):
            if isinstance(operand, ast.NameConstant) and operand.value is None:
                return {}
            else:
                raise TyError("Invalid operand pattern.", operand)
        else:
            raise TyError("Invalid operand pattern.", operand)

    @classmethod
    def trans_pat_UnaryOp(cls, ctx, pat, idx, scrutinee_tr):
        op, operand = pat.op, pat.operand
        if isinstance(op, (ast.USub, ast.UAdd)):
            condition = ast.copy_location(
                ast.Compare(
                    left=scrutinee_tr,
                    ops=[ast.Eq()],
                    comparators=[pat]),
                pat)
        else: # not None
            condition = ast.copy_location(
                ast.Compare(
                    left=scrutinee_tr,
                    ops=[ast.IsNot()],
                    comparators=[
                        ast.copy_location(
                            ast.NameConstant(None),
                            pat)]),
                pat)
        return condition, {}
   
    @classmethod
    def ana_Str(cls, ctx, e, idx):
        return

    @classmethod
    def trans_Str(cls, ctx, e, idx):
        return ast.copy_location(
            ast.Str(s=e.s),
            e)

    @classmethod
    def ana_pat_Str(cls, ctx, pat, idx):
        return {}

    @classmethod
    def trans_pat_Str(cls, ctx, pat, idx, scrutinee_tr):
        condition = ast.copy_location(
            ast.Compare(
                left=scrutinee_tr,
                ops=[ast.Eq()],
                comparators=[ast.copy_location(
                    ast.Str(s=pat.s),
                    pat)]),
            pat)
        return condition, {}

    @classmethod
    def ana_JoinedStr(cls, ctx, e, idx):
        values = e.values
        for value in values:
            if isinstance(value, ast.Str): continue
            else: # FormattedValue
                fvalue = value.value
                ctx.ana(fvalue, py_type)
                format_spec = value.format_spec
                if format_spec is not None:
                    ctx.ana(format_spec, py_type)

    @classmethod
    def trans_JoinedStr(cls, ctx, e, idx):
        return ast.copy_location(
            ast.JoinedStr(
                values=[
                    ast.copy_location(ast.Str(s=value.s), value)
                    if isinstance(value, ast.Str) else 
                    ast.copy_location(
                        ast.FormattedValue(
                            value=ctx.trans(value.value),
                            conversion=value.conversion,
                            format_spec=(
                                None 
                                if value.format_spec is None else
                                ctx.trans(value.format_spec))),
                        value)
                    for value in e.values]),
            e)

    @classmethod
    def ana_FormattedValue(cls, ctx, e, idx):
        pretend_e = e.pretend_e = ast.copy_location(
            ast.JoinedStr(
                values=[e]), e)
        return cls.ana_JoinedStr(ctx, pretend_e, idx)

    @classmethod
    def trans_FormattedValue(cls, ctx, e, idx):
        return cls.trans_JoinedStr(ctx, e.pretend_e, idx)

    @classmethod
    def ana_pat_JoinedStr(cls, ctx, pat, idx):
        return string.ana_pat_JoinedStr(ctx, pat, idx)

    @classmethod
    def trans_pat_JoinedStr(cls, ctx, pat, idx, scrutinee_tr):
        str_condition, binding_translations = \
            string.trans_pat_JoinedStr(ctx, pat, idx, scrutinee_tr)
        cls_condition = ast.fix_missing_locations(ast.copy_location(
            astx.builtin_call('isinstance', []), pat))
        cls_condition.args.append(scrutinee_tr)
        cls_condition.args.append(
            ast.fix_missing_locations(ast.copy_location(ast.Attribute(
                value=ast.Name(id="__builtins__", ctx=astx.load_ctx),
                attr="str",
                ctx=astx.load_ctx), pat))
        )
        condition = ast.copy_location(
            ast.BoolOp(
                op=ast.And(),
                values=[cls_condition, str_condition]),
            pat)
        return condition, binding_translations

    @classmethod
    def ana_pat_FormattedValue(cls, ctx, pat, idx):
        pat.pretend_pat = pretend_pat = ast.copy_location(
            ast.JoinedStr(values=[pat]), pat)
        return cls.ana_pat_JoinedStr(ctx, pretend_pat, idx)
            
    @classmethod
    def trans_pat_FormattedValue(cls, ctx, pat, idx, scrutinee_trans):
        return cls.trans_pat_JoinedStr(ctx, pat.pretend_pat, idx, 
                                       scrutinee_trans)

    @classmethod
    def ana_NameConstant(cls, ctx, e, idx):
        return

    @classmethod
    def trans_NameConstant(cls, ctx, e, idx):
        return ast.copy_location(
            ast.NameConstant(value=e.value),
            e)

    @classmethod
    def ana_pat_NameConstant(cls, ctx, pat, idx):
        return {}

    @classmethod
    def trans_pat_NameConstant(cls, ctx, pat, idx, scrutinee_tr):
        condition = ast.copy_location(
            ast.Compare(
                left=scrutinee_tr,
                ops=[ast.Is()],
                comparators=[
                    ast.copy_location(
                        ast.NameConstant(pat.value),
                        pat)]),
            pat)
        return condition, {}

    @classmethod
    def ana_Name(cls, ctx, e, idx):
        id = e.id
        if id == 'NotImplemented' or id == 'Ellipsis':
            return
        else:
            raise TyError("Invalid constant of type py.", e) # TODO defer to lifting

    @classmethod
    def trans_Name(cls, ctx, e, idx):
        return ast.copy_location(
            ast.Name(
                id=e.id,
                ctx=e.ctx),
            e)

    @classmethod
    def ana_pat_Name(cls, ctx, pat, idx):
        id = pat.id
        if id == 'NotImplemented' or id == 'Ellipsis':
            return {}
        else:
            raise TyError("Invalid constant pattern of type py.", pat)

    @classmethod
    def trans_pat_Name(cls, ctx, pat, idx, scrutinee_tr):
        condition = ast.copy_location(
            ast.Compare(
                left=scrutinee_tr,
                ops=[ast.Eq()],
                comparators=[
                    ast.copy_location(
                        ast.Name(id=pat.id, ctx=pat.ctx),
                        pat)]),
            pat)
        return condition, {}

    @classmethod
    def ana_Dict(cls, ctx, e, idx):
        for key, val in zip(e.keys, e.values):
            ctx.ana(key, py_type)
            ctx.ana(val, py_type)

    @classmethod
    def trans_Dict(cls, ctx, e, idx):
        return ast.copy_location(
            ast.Dict(
                keys=[ctx.trans(key)
                      for key in e.keys],
                values=[ctx.trans(val)
                        for val in e.values]),
            e)

    @classmethod
    def ana_pat_Dict(cls, ctx, pat, idx):
        used_keys = set()
        bindings = { }
        for key, value in zip(pat.keys, pat.values):
            if isinstance(key, ast.Str):
                key.id = key_id = key.s
            elif isinstance(key, ast.Name):
                key_id = key.id
            else:
                raise TyError("Invalid key in dict pattern.", key)
            if key_id in used_keys:
                raise TyError(
                    "Duplicate key.", key)
            used_keys.add(key_id)
            new_bindings = ctx.ana_pat(value, py_type)
            _update_name_bindings_disjoint(bindings, new_bindings)
        return bindings

    @classmethod
    def trans_pat_Dict(cls, ctx, pat, idx, scrutinee_trans):
        # ('a', 'b', 'c') == tuple(scrutinee_trans.keys())
        dict_condition = ast.fix_missing_locations(ast.copy_location(
            astx.isinstance_builtin_id(scrutinee_trans, 'dict'),
            pat))
        keys_condition = ast.fix_missing_locations(ast.copy_location(
            ast.Compare(
                left=ast.Set(
                    elts=[
                        ast.Str(s=key.id)
                        for key in pat.keys
                    ]),
                ops=[ast.Eq()],
                comparators=[
                    astx.builtin_call(
                        'set',
                        [
                            ast.Call(
                                func=ast.Attribute(
                                    value=scrutinee_trans,
                                    attr='keys',
                                    ctx=astx.load_ctx),
                                args=[],
                                keywords=[])]),
                ]),
            pat))
        conditions = [dict_condition, keys_condition]
        binding_translations = { }
        for key, value in zip(pat.keys, pat.values):
            cur_scrutinee_tr = ast.fix_missing_locations(ast.copy_location(
                ast.Subscript(
                    value=scrutinee_trans,
                    slice=ast.Index(value=ast.Str(s=key.id)),
                    ctx=astx.load_ctx),
                key))
            cur_condition, cur_binding_translations = \
                ctx.trans_pat(value, cur_scrutinee_tr)
            conditions.append(cur_condition)
            binding_translations.update(cur_binding_translations)
        condition = ast.copy_location(
            ast.BoolOp(
                op=ast.And(),
                values=conditions),
            pat)
        return condition, binding_translations

    @classmethod
    def ana_Set(cls, ctx, e, idx):
        for elt in e.elts:
            ctx.ana(elt, py_type)

    @classmethod
    def trans_Set(cls, ctx, e, idx):
        return ast.copy_location(
            ast.Set(
                elts=[
                    ctx.trans(elt)
                    for elt in e.elts]),
            e)

    @classmethod
    def ana_List(cls, ctx, e, idx):
        for elt in e.elts:
            ctx.ana(elt, py_type)

    @classmethod
    def trans_List(cls, ctx, e, idx):
        return ast.copy_location(
            ast.List(
                elts=[
                    ctx.trans(elt)
                    for elt in e.elts],
                ctx=e.ctx),
            e)

    @classmethod
    def ana_pat_List(cls, ctx, pat, idx):
        bindings = { }
        for elt in pat.elts:
            new_bindings = ctx.ana_pat(elt, py_type)
            _update_name_bindings_disjoint(bindings, new_bindings)
        return bindings

    @classmethod
    def trans_pat_List(cls, ctx, pat, idx, scrutinee_trans):
        list_condition = ast.fix_missing_locations(ast.copy_location(
            astx.isinstance_builtin_id(scrutinee_trans, 'list'),
            pat))
        length_condition = ast.fix_missing_locations(ast.copy_location(
            ast.Compare(
                left=astx.builtin_call('len', [scrutinee_trans]),
                ops=[ast.Eq()],
                comparators=[ast.Num(n=len(pat.elts))]),
            pat))
        conditions = [list_condition, length_condition]
        binding_translations = { }
        for i, elt in enumerate(pat.elts):
            elt_scrutinee_trans = ast.fix_missing_locations(ast.copy_location(
                ast.Subscript(
                    value=scrutinee_trans,
                    slice=ast.Index(value=ast.Num(n=i)),
                    ctx=astx.load_ctx),
                elt))
            elt_condition, elt_binding_translations = \
                ctx.trans_pat(elt, elt_scrutinee_trans)
            conditions.append(elt_condition)
            binding_translations.update(elt_binding_translations)
        
        condition = ast.copy_location(
            ast.BoolOp(
                op=ast.And(),
                values=conditions),
            pat)
        return condition, binding_translations

    @classmethod
    def ana_Tuple(cls, ctx, e, idx):
        for elt in e.elts:
            ctx.ana(elt, py_type)

    @classmethod
    def trans_Tuple(cls, ctx, e, idx):
        return ast.copy_location(
            ast.Tuple(
                elts=[
                    ctx.trans(elt)
                    for elt in e.elts],
                ctx=e.ctx),
            e)

    @classmethod
    def ana_pat_Tuple(cls, ctx, pat, idx):
        bindings = { }
        for elt in pat.elts:
            new_bindings = ctx.ana_pat(elt, py_type)
            _update_name_bindings_disjoint(bindings, new_bindings)
        return bindings
    
    @classmethod
    def trans_pat_Tuple(cls, ctx, pat, idx, scrutinee_trans):
        return cls._trans_pat_Tuple(ctx, pat, pat, 
                                   None, None, 
                                   None, scrutinee_trans)

    @classmethod
    def _trans_pat_Tuple(cls, ctx, pat, tpl_pat, 
                         extender, extender_on_right, 
                         binder, 
                         scrutinee_trans):
        tuple_condition = ast.fix_missing_locations(ast.copy_location(
            astx.isinstance_builtin_id(scrutinee_trans, 'tuple'),
            pat))
        length_condition = ast.fix_missing_locations(ast.copy_location(
            ast.Compare(
                left=astx.builtin_call('len', [scrutinee_trans]),
                ops=[ast.Eq() if extender is None else ast.GtE()],
                comparators=[ast.Num(n=len(tpl_pat.elts))]),
            pat))
        conditions = [tuple_condition, length_condition]

        binding_translations = { }
        elts = tpl_pat.elts
        n_elts = len(elts)
        for i, elt in enumerate(elts):
            elt_scrutinee_trans = ast.fix_missing_locations(ast.copy_location(
                ast.Subscript(
                    value=scrutinee_trans,
                    slice=ast.Index(
                        value=ast.Num(
                            n=i if extender is None or extender_on_right else -n_elts + i)),
                    ctx=astx.load_ctx),
                elt))
            elt_condition, elt_binding_translations = \
                ctx.trans_pat(elt, elt_scrutinee_trans)
            conditions.append(elt_condition)
            binding_translations.update(elt_binding_translations)
        
        if extender is not None:
            if extender_on_right:
                extender_slice = ast.Slice(
                    lower=ast.Num(n_elts),
                    upper=None,
                    step=None)
            else:
                extender_slice = ast.Slice(
                    lower=None,
                    upper=ast.Num(n=-n_elts),
                    step=None)
            extender_translation = ast.fix_missing_locations(ast.copy_location(
                ast.Subscript(
                    value=scrutinee_trans,
                    slice=extender_slice,
                    ctx=astx.load_ctx),
                pat))
            binding_translations[extender.id] = extender_translation

        if binder is not None:
            if extender is None:
                binder_translation = scrutinee_trans
            else:
                if extender_on_right:
                    binder_slice = ast.Slice(
                        lower=None,
                        upper=ast.Num(n=n_elts),
                        step=None)
                else:
                    binder_slice = ast.Slice(
                        lower=ast.Num(n=-n_elts),
                        upper=None,
                        step=None)
                binder_translation = ast.fix_missing_locations(ast.copy_location(
                    ast.Subscript(
                        value=scrutinee_trans,
                        slice=binder_slice,
                        ctx=astx.load_ctx),
                    pat))
            binding_translations[binder.id] = binder_translation

        condition = ast.copy_location(
            ast.BoolOp(
                op=ast.And(),
                values=conditions),
            pat)

        return condition, binding_translations

    @classmethod
    def ana_Ellipsis(cls, ctx, e, idx):
        return

    @classmethod
    def trans_Ellipsis(cls, ctx, e, idx):
        return ast.copy_location(
            ast.Ellipsis(),
            e)
    
    @classmethod
    def ana_Bytes(cls, ctx, e, idx):
        return

    @classmethod
    def trans_Bytes(cls, ctx, e, idx):
        return ast.copy_location(
            ast.Bytes(s=e.s),
            e)

    @classmethod
    def ana_pat_Bytes(cls, ctx, pat, idx):
        return {}

    @classmethod
    def trans_pat_Bytes(cls, ctx, pat, idx, scrutinee_tr):
        condition = ast.copy_location(
            ast.Compare(
                left=scrutinee_tr,
                ops=[ast.Eq()],
                comparators=[ast.copy_location(
                    ast.Bytes(s=pat.s),
                    pat)]),
            pat)
        return condition, {}

    @classmethod
    def syn_FunctionDef(cls, ctx, stmt):
        cls.ana_FunctionDef(ctx, stmt, ())
        return py_type

    @classmethod
    def ana_FunctionDef(cls, ctx, stmt, idx):
        # process decorators
        decorator_list = stmt.decorator_list
        if hasattr(stmt, "fragment_ascription"):
            decorator_list = decorator_list[1:]
        if len(decorator_list) > 0:
            for decorator in decorator_list:
                ctx.ana(decorator, py_type)

        # process arguments
        def _process_arg(arg):
            annotation = arg.annotation
            if annotation is not None:
                ctx.ana(annotation, py_type)
            name = ast.Name(id=arg.arg,
                            lineno=arg.lineno,
                            col_offset=arg.col_offset)
            return (name, py_type)
        def _process_args():
            arguments = stmt.args
            for arg in arguments.args:
                yield _process_arg(arg)
            vararg = arguments.vararg
            if vararg is not None:
                yield _process_arg(vararg)
            kwonlyargs = arguments.kwonlyargs
            if kwonlyargs is not None:
                for kwonlyarg in kwonlyargs:
                    yield _process_arg(kwonlyarg)
            kw_defaults = arguments.kw_defaults
            if kw_defaults is not None:
                for kw_default in kw_defaults:
                    ctx.ana(kw_default, py_type)
            kwarg = arguments.kwarg
            if kwarg is not None:
                yield _process_arg(kwarg)
            defaults = arguments.defaults
            if defaults is not None:
                for default in defaults:
                    ctx.ana(default, py_type)
        arg_sig = stmt.arg_sig = OrderedDict(_process_args())

        # return annotation
        returns = stmt.returns
        if returns is not None:
            ctx.ana(returns, py_type)

        # push bindings
        self_name = ast.copy_location(
            ast.Name(id=stmt.name),
            stmt)
        ctx.push_var_bindings({self_name : py_type})
        uniq_arg_sig = { }
        for name, ty in arg_sig.items():
            id = name.id
            ctx.add_id_var_binding(id, id, ty)
            uniq_arg_sig[id] = (id, ty)
        stmt.uniq_arg_sig = uniq_arg_sig

        # process docstring
        body = stmt.body
        if (len(body) > 1 
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Str)):
            proper_body = stmt.proper_body = body[1:]
            docstring = stmt.docstring = body[0].value.s
        else:
            proper_body = stmt.proper_body = body
            docstring = stmt.docstring = None

        # check statements in proper_body
        proper_body_block = stmt.proper_body_block = _terms.Block(proper_body)
        ctx.ana_block(proper_body_block, py_type)

        # bindings
        ctx.pop_var_bindings()

    @classmethod
    def trans_FunctionDef(cls, ctx, stmt, idx, mechanism):
        uniq_id = stmt.uniq_id

        # translate arguments
        args = stmt.args
        arguments_tr = ast.arguments(
            args= [
                ast.arg(
                    arg=stmt.uniq_arg_sig[arg.arg][0],
                    annotation=None if arg.annotation is None else ctx.trans(arg.annotation),
                    lineno=arg.lineno,
                    col_offset=arg.col_offset)
                for arg in args.args
            ],
            vararg=None if args.vararg is None else ast.copy_location(
                ast.arg(
                    arg=args.vararg.arg,
                    annotation=None if args.vararg.annotation is None 
                      else ctx.trans(args.vararg.annotation)), args.vararg),
            kwonlyargs=[
                ast.copy_location(
                    ast.arg(
                        arg=arg.arg,
                        annotation=None if arg.annotation is None 
                          else ctx.trans(arg.annotation)), arg)
                for arg in args.kwonlyargs
            ],
            kw_defaults=[
                ctx.trans(kw_default) 
                for kw_default in args.kw_defaults
            ],
            kwarg=None if args.kwarg is None else ast.copy_location(
                ast.arg(
                    arg=args.kwarg.arg,
                    annotation=None if args.kwarg.annotation is None
                      else ctx.trans(args.kwarg.annotation)), args.kwarg),
            defaults=[
                ctx.trans(default)
                for default in args.defaults
            ])

        # translate body
        body_tr = ctx.trans_block(stmt.proper_body_block, 
                                  BlockTransMechanism.Return)

        return [ast.copy_location(
            ast.FunctionDef(
                name=uniq_id,
                args=arguments_tr,
                body=body_tr,
                decorator_list=[],
                returns=None), 
            stmt)]

    @classmethod
    def integrate_static_FunctionDef(cls, ctx, stmt):
        name_ast = ast.copy_location(
            ast.Name(id=stmt.name, ctx=astx.load_ctx),
            stmt)
        stmt.uniq_bindings = uniq_bindings = ctx.add_bindings({ name_ast: stmt.ty })
        stmt.uniq_id = uniq_bindings[stmt.name][0]

    @classmethod
    def integrate_trans_FunctionDef(cls, ctx, stmt, translation, mechanism):
        uniq_id = stmt.uniq_id
        if mechanism == BlockTransMechanism.Return:
            translation.append(ast.copy_location(
                ast.Return(
                    value=ast.copy_location(
                        ast.Name(
                            id=uniq_id,
                            ctx=astx.load_ctx),
                        stmt)),
                stmt))

    @classmethod
    def ana_Lambda(cls, ctx, e, idx):
        # process args
        arguments = e.args
        for default in arguments.defaults:
            ctx.ana(default, py_type)
        for default in arguments.kw_defaults:
            ctx.ana(default, py_type)

        def _process_arg(arg):
            name = ast.Name(id=arg.arg,
                            lineno=arg.lineno,
                            col_offset=arg.col_offset)
            return (name, py_type)
        def _process_args():
            for arg in arguments.args:
                yield _process_arg(arg)
            vararg = arguments.vararg
            if vararg is not None:
                yield _process_arg(vararg)
            kwonlyargs = arguments.kwonlyargs
            if kwonlyargs is not None:
                for kwonlyarg in kwonlyargs:
                    yield _process_arg(kwonlyarg)
            kwarg = arguments.kwarg
            if kwarg is not None:
                yield _process_arg(kwarg)
        arg_sig = e.arg_sig = OrderedDict(_process_args())

        # push bindings
        ctx.push_var_bindings({})
        uniq_arg_sig = { }
        for name, ty in arg_sig.items():
            id = name.id
            ctx.add_id_var_binding(id, id, ty)
            uniq_arg_sig[id] = (id, ty)
        e.uniq_arg_sig = uniq_arg_sig

        # body
        ctx.ana(e.body, py_type)
        
        ctx.pop_var_bindings()

    @classmethod
    def trans_Lambda(cls, ctx, e, idx):

        # translate arguments
        args = e.args
        arguments_tr = ast.arguments(
            args=args.args,
            vararg=args.vararg,
            kwonlyargs=args.kwonlyargs,
            kw_defaults=[
                ctx.trans(kw_default) 
                for kw_default in args.kw_defaults
            ],
            kwarg=args.kwarg,
            defaults=[
                ctx.trans(default)
                for default in args.defaults
            ])
        
        # translate body
        body_tr = ctx.trans(e.body)

        return ast.copy_location(
            ast.Lambda(
                args=arguments_tr,
                body=body_tr), e)

    @classmethod
    def ana_DictComp(cls, ctx, e, idx):
        generators = e.generators
        for generator in generators:
            ctx.ana(generator.iter, py_type)
            target = generator.target
            bindings = ctx.ana_pat(generator.target, py_type)
            var_bindings = ctx.push_var_bindings(bindings)
            generator.var_bindings = var_bindings
            for cond in generator.ifs:
                ctx.ana(cond, py_type)
        ctx.ana(e.key, py_type)
        ctx.ana(e.value, py_type)
        for generator in generators:
            ctx.pop_var_bindings()

    @classmethod
    def trans_DictComp(cls, ctx, e, idx):
        return ast.copy_location(
            ast.DictComp(
                key=ctx.trans(e.key),
                value=ctx.trans(e.value),
                generators=[
                    ast.comprehension(
                        target=cls._trans_simple_pat(ctx, 
                                                     generator.var_bindings, 
                                                     generator.target),
                        iter=ctx.trans(generator.iter),
                        ifs=[ctx.trans(cond) 
                             for cond in generator.ifs],
                        is_async=generator.is_async)
                    for generator in e.generators]),
            e)

    @classmethod
    def _trans_simple_pat(cls, ctx, var_bindings, target):
        if isinstance(target, ast.Tuple):
            return ast.copy_location(
                ast.Tuple(
                    elts=[
                        cls._trans_simple_pat(ctx, elt)
                        for elt in target.elts],
                    ctx=target.ctx),
                target)
        elif isinstance(target, ast.List):
            return ast.copy_location(
                ast.List(
                    elts=[
                        cls._trans_simple_pat(ctx, elt)
                        for elt in target.elts],
                    ctx=target.ctx),
                target)
        elif isinstance(target, ast.Name):
            return ast.copy_location(
                ast.Name(
                    id=var_bindings[target.id][0],
                    ctx=target.ctx),
                target)
        else:
            raise TyError("Invalid pattern form in generator.", target)

    @classmethod
    def ana_SetComp(cls, ctx, e, idx):
        generators = e.generators
        for generator in generators:
            ctx.ana(generator.iter, py_type)
            target = generator.target
            bindings = ctx.ana_pat(generator.target, py_type)
            var_bindings = ctx.push_var_bindings(bindings)
            generator.var_bindings = var_bindings
            for cond in generator.ifs:
                ctx.ana(cond, py_type)
        ctx.ana(e.elt, py_type)
        for generator in generators:
            ctx.pop_var_bindings()

    @classmethod
    def trans_SetComp(cls, ctx, e, idx):
        return ast.copy_location(
            ast.SetComp(
                elt=ctx.trans(e.elt),
                generators=[
                    ast.comprehension(
                        target=cls._trans_simple_pat(ctx, 
                                                     generator.var_bindings, 
                                                     generator.target),
                        iter=ctx.trans(generator.iter),
                        ifs=[ctx.trans(cond) 
                             for cond in generator.ifs],
                        is_async=generator.is_async)
                    for generator in e.generators]),
            e)

    @classmethod
    def ana_ListComp(cls, ctx, e, idx):
        generators = e.generators
        for generator in generators:
            ctx.ana(generator.iter, py_type)
            target = generator.target
            bindings = ctx.ana_pat(generator.target, py_type)
            var_bindings = ctx.push_var_bindings(bindings)
            generator.var_bindings = var_bindings
            for cond in generator.ifs:
                ctx.ana(cond, py_type)
        ctx.ana(e.elt, py_type)
        for generator in generators:
            ctx.pop_var_bindings()

    @classmethod
    def trans_ListComp(cls, ctx, e, idx):
        return ast.copy_location(
            ast.ListComp(
                elt=ctx.trans(e.elt),
                generators=[
                    ast.comprehension(
                        target=cls._trans_simple_pat(ctx, 
                                                     generator.var_bindings, 
                                                     generator.target),
                        iter=ctx.trans(generator.iter),
                        ifs=[ctx.trans(cond) 
                             for cond in generator.ifs],
                        is_async=generator.is_async)
                    for generator in e.generators]),
            e)

    @classmethod
    def ana_GeneratorExp(cls, ctx, e, idx):
        generators = e.generators
        for generator in generators:
            ctx.ana(generator.iter, py_type)
            target = generator.target
            bindings = ctx.ana_pat(generator.target, py_type)
            var_bindings = ctx.push_var_bindings(bindings)
            generator.var_bindings = var_bindings
            for cond in generator.ifs:
                ctx.ana(cond, py_type)
        ctx.ana(e.elt, py_type)
        for generator in generators:
            ctx.pop_var_bindings()

    @classmethod
    def trans_GeneratorExp(cls, ctx, e, idx):
        return ast.copy_location(
            ast.GeneratorExp(
                elt=ctx.trans(e.elt),
                generators=[
                    ast.comprehension(
                        target=cls._trans_simple_pat(ctx, 
                                                     generator.var_bindings, 
                                                     generator.target),
                        iter=ctx.trans(generator.iter),
                        ifs=[ctx.trans(cond) 
                             for cond in generator.ifs],
                        is_async=generator.is_async)
                    for generator in e.generators]),
            e)

    @classmethod
    def syn_BoolOp(cls, ctx, e):
        for value in e.values:
            ctx.ana(value, py_type)
        return py_type

    @classmethod
    def ana_BoolOp(cls, ctx, e, idx):
        for value in e.values:
            ctx.ana(value, py_type)

    @classmethod
    def trans_BoolOp(cls, ctx, e, idx=None):
        return ast.copy_location(
            ast.BoolOp(
                op=e.op,
                values=[ctx.trans(value)
                        for value in e.values]),
            e)

    @classmethod
    def syn_BinOp(cls, ctx, e):
        ctx.ana(e.left, py_type)
        ctx.ana(e.right, py_type)
        return py_type

    @classmethod
    def trans_BinOp(cls, ctx, e):
        return ast.copy_location(
            ast.BinOp(
                left=ctx.trans(e.left),
                op=e.op,
                right=ctx.trans(e.right)),
            e)

    @classmethod
    def ana_pat_BinOp(cls, ctx, pat, idx):
        left, op, right = pat.left, pat.op, pat.right
        if isinstance(op, ast.Add):
            if isinstance(left, ast.Str) or isinstance(right, ast.Str):
                pretend_pat = ast.fix_missing_locations(ast.copy_location(
                    ast.Call(
                        func=ast.Name(id="str", ctx=astx.load_ctx),
                        args=[],
                        keywords=[]),
                    pat))
                pretend_pat.args.append(astx.deep_copy_node(pat))
                pat._pretend_pat = pretend_pat
                return ctx.ana_pat(pretend_pat, py_type)
            else:
                if isinstance(left, ast.Tuple) and isinstance(right, ast.Name):
                    extender = right
                    extender_on_right = True
                    binder_pat = None
                    tuple_pat = left
                elif isinstance(right, ast.Tuple) and isinstance(left, ast.Name):
                    extender = left
                    extender_on_right = False
                    binder_pat = None
                    tuple_pat = right
                elif cls._is_Tuple_binder(left) and isinstance(right, ast.Name):
                    extender = right
                    extender_on_right = True
                    binder_pat = left
                    tuple_pat = left.func
                elif cls._is_Tuple_binder(right) and isinstance(left, ast.Name):
                    extender = left
                    extender_on_right = False
                    binder_pat = right
                    tuple_pat = right.func
                else:
                    raise TyError("Invalid pattern.", pat)
                pat._extender = extender
                pat._extender_on_right = extender_on_right
                pat._binder_pat = binder_pat
                pat._tuple_pat = tuple_pat
                if binder_pat is None:
                    tuple_bindings = ctx.ana_pat(tuple_pat, py_type)
                    pat._binder = None
                else:
                    tuple_bindings = ctx.ana_pat(binder_pat, py_type)
                    pat._binder = binder_pat.args[0]
                bindings = dict(tuple_bindings)
                _update_name_bindings_disjoint(bindings, { extender : py_type })
                return bindings
        else:
            raise TyError("Invalid pattern.", pat)

    @classmethod
    def trans_pat_BinOp(cls, ctx, pat, idx, scrutinee_trans):
        try: pretend_pat = pat._pretend_pat
        except AttributeError:
            return cls._trans_pat_Tuple(
                ctx, pat, pat._tuple_pat, 
                pat._extender, pat._extender_on_right, 
                pat._binder, 
                scrutinee_trans)
        else:
            return ctx.trans_pat(pretend_pat, scrutinee_trans)

    @classmethod
    def syn_UnaryOp(cls, ctx, e, idx):
        ctx.ana(e.operand, py_type)
        return py_type

    @classmethod
    def syn_Compare(cls, ctx, e):
        ctx.ana(e.left, py_type)
        for comparator in e.comparators:
            ctx.ana(comparator, py_type)
        return py_type

    @classmethod
    def trans_Compare(cls, ctx, e):
        return ast.copy_location(
            ast.Compare(
                left=ctx.trans(e.left),
                ops=e.ops,
                comparators=[
                    ctx.trans(comparator)
                    for comparator in e.comparators]),
            e)

    @classmethod
    def syn_IfExp(cls, ctx, e, idx):
        body_ty = ctx.syn(e.body)
        ctx.ana(e.orelse, body_ty)
        return body_ty

    @classmethod
    def ana_IfExp(cls, ctx, e, idx, ty):
        ctx.ana(e.body, ty)
        ctx.ana(e.orelse, ty)

    @classmethod
    def trans_IfExp(cls, ctx, e, idx):
        return ast.copy_location(
            ast.IfExp(
                test=ctx.trans(e.test),
                body=ctx.trans(e.body),
                orelse=ctx.trans(e.orelse)),
            e)

    @classmethod
    def syn_Call(cls, ctx, e, idx):
        for arg in e.args:
            if isinstance(arg, ast.Starred):
                ctx.ana(arg.value, py_type)
            else:
                ctx.ana(arg, py_type)
        used_kws = set()
        for keyword in e.keywords:
            kw_arg, kw_value = keyword.arg, keyword.value
            if kw_arg in used_kws:
                raise TyError("Duplicate keyword arguments.", kw_value)
            used_kws.add(kw_arg)
            ctx.ana(kw_value, py_type)
        return py_type
        
    @classmethod
    def trans_Call(cls, ctx, e, idx):
        return ast.copy_location(
            ast.Call(
                func=ctx.trans(e.func),
                args=[
                    ast.copy_location(
                        ast.Starred(
                            value=ctx.trans(arg.value),
                            ctx=arg.ctx),
                        arg) 
                    if isinstance(arg, ast.Starred) 
                    else ctx.trans(arg)
                for arg in e.args],
                keywords=[
                    ast.keyword(
                        arg=kw.arg,
                        value=ctx.trans(kw.value))
                    for kw in e.keywords]),
            e)

    @classmethod
    def _is_Tuple_binder(cls, pat):
        return (isinstance(pat, ast.Call) and 
                isinstance(pat.func, ast.Tuple) and 
                len(pat.args) == 1 and 
                isinstance(pat.args[0], ast.Name))

    @classmethod
    def ana_pat_Call(cls, ctx, pat, idx):
        func, args, keywords = pat.func, pat.args, pat.keywords
        pat._is_instance_pattern = False
        if isinstance(func, ast.Name):
            func_id = func.id
            if func_id == "str":
                if len(args) == 1 and len(keywords) == 0:
                    return ctx.ana_pat(args[0], string_ty)
                else:
                    raise TyError("Too many arguments in pattern.", pat)
            elif func_id == "int":
                if len(args) == 1 and len(keywords) == 0:
                    return ctx.ana_pat(args[0], num_ty)
                else:
                    raise TyError("Too many arguments in pattern.", pat)
            elif func_id == "float":
                if len(args) == 1 and len(keywords) == 0:
                    return ctx.ana_pat(args[0], ieee_ty)
                else:
                    raise TyError("Too many arguments in pattern.", pat)
            elif func_id == "bool" and len(keywords) == 0:
                if len(args) == 1:
                    return ctx.ana_pat(args[0], boolean_ty)
                else:
                    raise TyError("Too many arguments in pattern.", pat)
        elif isinstance(func, ast.Tuple):
            if len(args) == 1 and isinstance(args[0], ast.Name):
                func_bindings = ctx.ana_pat(func, py_type)
                bindings = dict(func_bindings)
                new_binding = { args[0] : CanonicalTy(tpl, OrderedDict(
                    (i, py_type)
                    for i in range(len(func.elts))
                )) }
                _update_name_bindings_disjoint(bindings, new_binding)
                return bindings
            else:
                raise TyError("Invalid pattern format.", pat)

        if len(args) == 0:
            pat._is_instance_pattern = True
            ctx.ana(func, py_type)
            used_keywords = set()
            bindings = {}
            for keyword in keywords:
                arg = keyword.arg
                if arg in used_keywords:
                    raise TyError("Duplicate keyword: " + arg, pat)
                used_keywords.add(arg)
                kw_bindings = ctx.ana_pat(keyword.value, py_type)
                _update_name_bindings_disjoint(bindings, kw_bindings)
            return bindings
        else:
            raise TyError("Invalid pattern.")

    @classmethod
    def trans_pat_Call(cls, ctx, pat, idx, scrutinee_trans):
        if pat._is_instance_pattern:
            cls_translation = ctx.trans(pat.func)
            cls_condition = ast.fix_missing_locations(ast.copy_location(
                astx.builtin_call('isinstance', []), pat))
            cls_condition.args.append(scrutinee_trans)
            cls_condition.args.append(cls_translation)
            conditions = [cls_condition]
            binding_translations = { } 
            for keyword in pat.keywords:
                arg = keyword.arg
                arg_scrutinee = ast.copy_location(
                    ast.Attribute(
                        value=scrutinee_trans,
                        attr=arg,
                        ctx=astx.load_ctx), 
                    pat)
                kw_condition, kw_binding_translations = \
                    ctx.trans_pat(keyword.value, arg_scrutinee)
                conditions.append(kw_condition)
                binding_translations.update(kw_binding_translations)
            condition = ast.copy_location(
                ast.BoolOp(
                    op=ast.And(),
                    values=conditions),
                pat)
        else:
            func = pat.func
            if isinstance(func, ast.Name):
                func_id = func.id
                if func_id == "str":
                    tag_condition = astx.isinstance_builtin_id(scrutinee_trans, 'str')
                elif func_id == "int":
                    tag_condition = astx.isinstance_builtin_id(scrutinee_trans, 'int')
                elif func_id == "float":
                    tag_condition = astx.isinstance_builtin_id(scrutinee_trans, 'float')
                elif func_id == "bool":
                    tag_condition = astx.isinstance_builtin_id(scrutinee_trans, 'bool')
                tag_condition = ast.fix_missing_locations(ast.copy_location(
                    tag_condition, pat))
                rec_condition, binding_translations = \
                    ctx.trans_pat(pat.args[0], scrutinee_trans)
                condition = ast.copy_location(
                    ast.BoolOp(
                        op=ast.And(),
                        values=[tag_condition, rec_condition]),
                    pat)
            else: # if isinstance(func, ast.Tuple):
                return cls._trans_pat_Tuple(ctx, pat, pat.func,
                                            None, None, 
                                            pat.args[0], 
                                            scrutinee_trans)
        return condition, binding_translations

    @classmethod
    def syn_Attribute(cls, ctx, e, idx):
        return py_type

    @classmethod
    def trans_Attribute(cls, ctx, e, idx):
        return ast.copy_location(
            ast.Attribute(
                value=ctx.trans(e.value),
                attr=e.attr,
                ctx=e.ctx),
            e)

    @classmethod
    def syn_Subscript(cls, ctx, e, idx):
        cls._ana_slice(ctx, e.slice)
        return py_type

    @classmethod
    def _ana_slice(cls, ctx, slice):
        if isinstance(slice, ast.Index):
            ctx.ana(slice.value, py_type)
        elif isinstance(slice, ast.Slice):
            lower, upper, step = slice.lower, slice.upper, slice.step
            if lower is not None and not astx.is_underscore(lower):
                ctx.ana(lower, py_type)
            if upper is not None and not astx.is_underscore(upper):
                ctx.ana(upper, py_type)
            if step is not None and not astx.is_underscore(step):
                ctx.ana(step, py_type)
        else: # ExtSlice
            for dim in slice.dims:
                cls._ana_slice(ctx, dim)

    @classmethod
    def trans_Subscript(cls, ctx, e, idx):
        return ast.copy_location(
            ast.Subscript(
                value=ctx.trans(e.value),
                slice=cls._trans_slice(ctx, e.slice),
                ctx=e.ctx),
            e)

    @classmethod
    def _trans_slice(cls, ctx, slice):
        if isinstance(slice, ast.Index):
            return ast.copy_location(
                ast.Index(
                    value=ctx.trans(slice.value)),
                slice)
        elif isinstance(slice, ast.Slice):
            lower, upper, step = slice.lower, slice.upper, slice.step
            lower_trans = (None if lower is None or astx.is_underscore(lower) 
                           else ctx.trans(lower))
            upper_trans = (None if upper is None or astx.is_underscore(upper)
                           else ctx.trans(upper))
            step_trans = (None if step is None or astx.is_underscore(step)
                          else ctx.trans(step))
            return ast.copy_location(
                ast.Slice(
                    lower=lower_trans,
                    upper=upper_trans,
                    step=step_trans),
                slice)
        else: # ExtSlice
            return ast.copy_location(
                ast.ExtSlice(
                    dims=[
                        cls._trans_slice(ctx, dim)
                        for dim in slice.dims]),
                slice)

py_type = CanonicalTy(py, ())

def _check_trivial_idx_ast(idx_ast):
    if (isinstance(idx_ast, ast.Index) and 
            isinstance(idx_ast.value, ast.Tuple) and 
            len(idx_ast.value.elts) == 0):
        return ()
    else:
        raise TypeValidationError(
            "unit type can only have trivial index.", idx_ast)

# TODO bytes
# TODO ilist
# TODO dict
# TODO mlist
# TODO complex?
# TODO decimal?

# Maybe not in the standard library?
# TODO proto
# TODO string_in
# TODO numpy stuff
# TODO cl stuff

