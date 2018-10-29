"""The typechecker and translator lives here."""
import ast  # Python standard library's abstract syntax module

import util.dicts
odict = util.dicts.odict # use ImmDict?
from _errors import ExtensionError, TyError, TypeMismatchError, OpInvalid
from _typelevel import Type, tycon
from _inctypes import IncompleteType

__all__ = (
    "Context",
)

class Context(object):
    def __init__(self, fn):
        self.fn = fn
        self.data = {}
        self._id_count = {}
        self._tmp_count = {}

    def generate_fresh_id(self, id):
        _id_count = self._id_count
        try:
            id_count = _id_count[id]
        except KeyError:
            _id_count[id] = 1
            return id
        else:
            _id_count[id] = id_count + 1
            return '__typy_id_' + id + '_' + str(id_count) + '__'
    
    def generate_fresh_tmp(self, tmp):
        _tmp_count = self._tmp_count
        print _tmp_count
        try:
            tmp_count = _tmp_count[tmp]
        except KeyError:
            tmp_count = _tmp_count[tmp] = 1
        else:
            tmp_count = _tmp_count[tmp] = tmp_count + 1
        return '__typy_tmp_' + tmp + '_' + str(tmp_count) + '__'

    def ana(self, e, ty):
        if not isinstance(ty, Type):
            raise ExtensionError(
                "Cannot analyze an expression against a non-type.")
        if _is_intro_form(e):
            e.is_intro_form = True
            classname = e.__class__.__name__
            if classname == "Name":
                classname = "Name_constructor"
            elif classname == "Call":
                classname = "Call_constructor"
            elif classname == "UnaryOp":
                classname = "Unary_Name_constructor"
            ana_method = 'ana_%s' % classname
            method = getattr(ty, ana_method)
            method(self, e)
            e.ty = ty
            e.delegate = ty
            e.translation_method_name = 'translate_%s' % classname
        elif _is_match_expr(e):
            e.is_match_expr = True
            delegate = tycon(self.fn.ascription)
            delegate.ana_match_expr(self, e, ty)
            e.ty = ty
            e.delegate = delegate
            e.translation_method_name = 'translate_match_expr'
        elif isinstance(e, ast.IfExp):
            delegate = tycon(self.fn.ascription)
            delegate.ana_IfExp(self, e, ty)
            e.ty = ty
            e.delegate = delegate
            e.translation_method_name = 'translate_IfExp'
        else:
            syn_ty = self.syn(e)
            if ty != syn_ty:
                raise TypeMismatchError(ty, syn_ty, e)

    def ana_intro_inc(self, value, inc_ty):
        if not _is_intro_form(value):
            raise ExtensionError("Term is not an intro form.")
        if not isinstance(inc_ty, IncompleteType):
            raise ExtensionError("No incomplete type provided.")
        classname = value.__class__.__name__
        if classname == "Name":
            classname = "Name_constructor"
        elif classname == "Call":
            classname = "Call_constructor"
        elif classname == "UnaryOp":
            classname = "Unary_Name_constructor"
        syn_idx_methodname = 'syn_idx_%s' % classname
        delegate = inc_ty.tycon
        method = getattr(delegate, syn_idx_methodname)
        syn_idx = method(self, value, inc_ty.inc_idx)
        ty = Type._construct_ty(delegate, syn_idx)
        value.is_intro_form = True
        value.translation_method_name = "translate_%s" % classname
        value.delegate, value.ty = delegate, ty
        return ty 

    def _process_ascription_slice(self, slice_):
        if isinstance(slice_, ast.Slice):
            lower, upper, step = slice_.lower, slice_.upper, slice_.step
            if lower is None and upper is not None and step is None:
                return self.parse_asc(upper)
        return None

    def parse_asc(self, asc_ast):
        if isinstance(asc_ast, ast.Name):
            # fn prims (in tydy, num, ieee, string)
            # type variables
            # environment variables
            # incomplete types
            raise NotImplementedError()
        elif isinstance(asc_ast, ast.UnaryOp):
            # type variables
            raise NotImplementedError()
        elif isinstance(asc_ast, ast.BinOp):
            # num * num * num
            # Nil + Cons(+a * list(+a))
            raise NotImplementedError()
        elif isinstance(asc_ast, ast.Dict):
            # product
            raise NotImplementedError()
        elif isinstance(asc_ast, ast.Set):
            # product?
            raise NotImplementedError()
        elif isinstance(asc_ast, ast.Compare):
            # fn
            raise NotImplementedError()
        elif isinstance(asc_ast, ast.Call):
            # ap
            raise NotImplementedError()
        elif isinstance(asc_ast, ast.Attribute):
            # projection
            raise NotImplementedError()
        elif isinstance(asc_ast, ast.Subscript):
            # tyop ap
            # inc tyop ap
            raise NotImplementedError()
        elif isinstance(asc_ast, ast.List):
            # ?
            raise NotImplementedError()
        elif isinstance(asc_ast, ast.Tuple):
            # (int, int, int)
            # perhaps you meant...
            raise NotImplementedError()
        else:
            raise NotImplementedError()

    def syn(self, e):
        if _is_match_expr(e):
            e.is_match_expr = True
            delegate = tycon(self.fn.ascription)
            ty = delegate.syn_match_expr(self, e)
            e.ty = ty
            e.delegate = delegate
            e.translation_method_name = "translate_match_expr"
        elif isinstance(e, ast.Subscript):
            value, slice_ = e.value, e.slice 
            ty = self._process_ascription_slice(slice_)
            if isinstance(ty, Type):
                self.ana(value, ty)
                delegate = value.delegate
                e.is_ascription = True 
            elif isinstance(ty, IncompleteType):
                if _is_intro_form(value):
                    self.ana_intro_inc(value, ty)
                    delegate, ty = value.delegate, value.ty
                    e.is_ascription = True 
                else:
                    raise TyError(
                        "Incomplete type ascriptions can only appear"
                        "on introductory forms.", 
                        value)
            else:
                # not an ascription
                delegate = self.syn(value)
                ty = delegate.syn_Subscript(self, e)
                e.translation_method_name = 'translate_Subscript'
        elif isinstance(e, ast.Name):
            delegate = tycon(self.fn.ascription)
            ty = delegate.syn_Name(self, e)
            if isinstance(ty, Type):
                e.translation_method_name = 'translate_Name'
            else:
                raise OpInvalid(
                    "syn_Name did not return a type.", e)
        elif isinstance(e, ast.Call):
            func = e.func
            delegate = self.syn(func)
            ty = delegate.syn_Call(self, e)
            if isinstance(ty, Type):
                e.translation_method_name = 'translate_Call'
            else:
                raise OpInvalid(
                    "syn_Call did not return a type.", e)
        elif isinstance(e, ast.UnaryOp):
            operand = e.operand
            delegate = self.syn(operand)
            ty = delegate.syn_UnaryOp(self, e)
            if isinstance(ty, Type):
                e.translation_method_name = 'translate_UnaryOp'
            else:
                raise OpInvalid(
                    "syn_UnaryOp did not return a type.", e)
        elif isinstance(e, ast.BinOp):
            left = e.left
            delegate = self.syn(left)
            ty = delegate.syn_BinOp(self, e)
            if isinstance(ty, Type):
                e.translation_method_name = 'translate_BinOp'
            else:
                raise OpInvalid(
                    "syn_BinOp did not return a type.", e)
        elif isinstance(e, ast.Compare):
            left, comparators = e.left, e.comparators
            delegate, match = None, None
            for e_ in util.tpl_cons(left, comparators):
                try:
                    delegate = self.syn(e_)
                    match = e_
                    break
                except TyError: 
                    continue
            if delegate is None:
                raise TyError("No comparators synthesize a type.", e)
            match.match = True
            ty = delegate.syn_Compare(self, e)
            if isinstance(ty, Type):
                e.translation_method_name = 'translate_Compare'
            else:
                raise OpInvalid(
                    "syn_Compare did not return a type.", e)
        elif isinstance(e, ast.BoolOp):
            values = e.values
            delegate, match = None, None
            for value in values:
                try:
                    delegate = self.syn(value)
                    match = value
                    break
                except TyError:
                    continue
            if delegate is None:
                raise TyError("No clauses of boolean operation synthesize a type.", e)
            match.match = True
            ty = delegate.syn_BoolOp(self, e)
            if isinstance(ty, Type):
                e.translation_method_name = 'translate_BoolOp'
            else:
                raise OpInvalid(
                    "syn_BoolOp did not return a type.", e)
        elif isinstance(e, ast.Attribute):
            value = e.value
            delegate = self.syn(value)
            ty = delegate.syn_Attribute(self, e)
            if isinstance(ty, Type):
                e.translation_method_name = 'translate_Attribute'
            else:
                raise OpInvalid(
                    "syn_Attribute did not return a type.", e)
        elif isinstance(e, ast.IfExp):
            delegate = tycon(self.fn.ascription)
            ty = delegate.syn_IfExp(self, e)
            if isinstance(ty, Type):
                e.translation_method_name = 'translate_IfExp'
            else:
                raise OpInvalid(
                    "syn_IfExp did not return a type.", e)
        else:
            raise TyError("Unsupported form for type synthesis: " + 
                          e.__class__.__name__, e)

        assert delegate is not None
        assert ty is not None 
        e.delegate, e.ty = delegate, ty
        return ty 

    def translate(self, tree):
        if hasattr(tree, "is_ascription"):
            translation = self.translate(tree.value)
        elif hasattr(tree, "is_match_expr"):
            delegate = tree.delegate
            translation = delegate.translate_match_expr(self, tree)
        elif hasattr(tree, "is_intro_form"):
            delegate = tree.ty
            method = getattr(delegate, tree.translation_method_name)
            translation = method(self, tree)
        elif isinstance(tree, ast.Name):
            delegate = self.fn.tree.ty
            translation = delegate.translate_Name(self, tree)
        elif isinstance(tree, (
                ast.Call, 
                ast.Subscript, 
                ast.Attribute, 
                ast.BoolOp, 
                ast.Compare, 
                ast.BinOp, 
                ast.UnaryOp,
                ast.IfExp)):
            delegate = tree.delegate
            method = getattr(delegate, tree.translation_method_name)
            translation = method(self, tree)
        else:
            method_name = tree.translation_method_name
            delegate = tree.ty
            method = getattr(delegate, method_name)
            translation = method(self, tree)
        return translation

    def ana_pat(self, pat, ty):
        if _is_pat_intro_form(pat):
            classname = pat.__class__.__name__
            if classname == "Name":
                classname = "Name_constructor"
            elif classname == "Call":
                classname = "Call_constructor"
            elif classname == "UnaryOp":
                classname = "Unary_Name_constructor"
            ana_pat_methodname = 'ana_pat_' + classname
            delegate = ty
            method = getattr(delegate, ana_pat_methodname)
            bindings = method(self, pat)
            if not isinstance(bindings, odict):
                raise ExtensionError("Expected ordered dict.")
            for name, binding_ty in bindings.iteritems():
                if not util.astx.is_identifier(name):
                    raise ExtensionError("Binding " + str(name) + " is not an identifier.")
                if not isinstance(binding_ty, Type):
                    raise ExtensionError("Binding for " + name + " has invalid type.")
        elif isinstance(pat, ast.Name):
            id = pat.id
            if id == "_":
                bindings = odict()
            else:
                bindings = odict((
                    (id, ty),
                ))
        else:
            raise TyError("Invalid pattern form", pat)
        pat.bindings = bindings
        pat.ty = ty
        return bindings

    def translate_pat(self, pat, scrutinee_trans):
        if _is_pat_intro_form(pat):
            classname = pat.__class__.__name__
            if classname == "Name":
                classname = "Name_constructor"
            elif classname == "Call":
                classname = "Call_constructor"
            elif classname == "UnaryOp":
                classname = "Unary_Name_constructor"
            translate_pat_methodname = "translate_pat_" + classname
            delegate = pat.ty
            method = getattr(delegate, translate_pat_methodname)
            condition, binding_translations = method(self, pat, scrutinee_trans)
        elif isinstance(pat, ast.Name):
            condition = ast.Name(id='True', ctx=ast.Load())
            id = pat.id
            if id == "_":
                binding_translations = odict()
            else:
                binding_translations = odict(((id, scrutinee_trans),))
        else:
            raise ExtensionError("Cannot translate this pattern...")
        bindings = pat.bindings
        if bindings.keys() != binding_translations.keys():
            raise ExtensionError("Not all bindings have translations.")
        return condition, binding_translations

    def ana_kind(self, tyexp, kind):
        tyexp.ana_kind(self, kind)

    def syn_kind(self, tyexp):
        return tyexp.syn_kind(self)

_intro_forms = (
    ast.FunctionDef, # only stmt intro form
    ast.Lambda, 
    ast.Dict, 
    ast.Set, 
    # TODO ast.ListComp, 
    # TODO ast.SetComp, 
    # TODO ast.DictComp, 
    # TODO ast.GeneratorExp, 
    ast.Num, 
    ast.Str, 
    ast.List, 
    ast.Tuple)
def _is_intro_form(e):
    return (isinstance(e, _intro_forms) or 
            _is_Name_constructor(e) or
            _is_Unary_Name_constructor(e) or 
            _is_Call_constructor(e))

_pat_intro_forms = (
    ast.Dict,
    ast.Set,
    ast.Num,
    ast.Str,
    ast.List,
    ast.Tuple)
def _is_pat_intro_form(pat):
    return (isinstance(pat, _pat_intro_forms) or
            _is_Name_constructor(pat) or 
            _is_Unary_Name_constructor(pat) or
            _is_Call_constructor(pat))

def _is_Name_constructor(e):
    return isinstance(e, ast.Name) and _is_Name_constructor_id(e.id)

def _is_Name_constructor_id(id):
    return id != "" and id[0].isupper()

def _is_Unary_Name_constructor(e):
    return (isinstance(e, ast.UnaryOp) and 
            isinstance(e.op, (ast.USub, ast.UAdd, ast.Invert)) and 
            _is_Name_constructor(e.operand))

def _is_Call_constructor(e):
    return isinstance(e, ast.Call) and _is_Name_constructor(e.func)

def _is_match_expr(e):
    # {scrutinee} bis {rules}
    return (isinstance(e, ast.Compare) and
            len(e.ops) == 1 and 
            isinstance(e.ops[0], ast.Is) and
            isinstance(e.left, ast.Set) and 
            isinstance(e.comparators[0], ast.Dict))

def _check_ascription_ast(e):
    if isinstance(e, ast.Subscript):
        value, slice = e.value, e.slice
        if isinstance(slice, ast.Slice):
            lower, upper, step = slice.lower, slice.upper, slice.step
            if lower is None and upper is not None and step is None:
                return value, upper

def _check_ascription(e, static_env):
    raise NotImplementedError()
    # if isinstance(e, ast.Subscript):
    #     value, slice = e.value, e.slice
    #     asc = _process_ascription_slice(slice, static_env)
    #     return value, asc
    # return None

def _process_asc_ast(ctx, asc_ast):
    asc = ctx.fn.static_env.eval_expr_ast(asc_ast)
    if (isinstance(asc, Type) or 
            isinstance(asc, IncompleteType)):
        return asc
    elif issubclass(asc, Type):
        return asc[...]
    else:
        raise TyError("Invalid ascription.", asc_ast)


