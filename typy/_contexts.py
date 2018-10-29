"""typy contexts"""

import ast
from . import util as _util
from .util import astx as _astx
from ._ty_exprs import (
    TyExprVar, TypeKind, SingletonKind, UName, 
    CanonicalTy, UCanonicalTy, UTyExpr, UProjection, 
    TyExprPrj)
from ._errors import UsageError, KindError, TyError
from ._fragments import is_fragment, Fragment
from . import _components
from . import _terms

__all__ = ("BlockTransMechanism", "Context")

class BlockTransMechanism:
    """An enumeration of translation mechanisms for blocks."""
    Statement = 1
    Return = 2
    class Assign(object):
        def __init__(self, target):
            self.target = target

from . import std
class Context(object):
    def __init__(self, static_env):
        self.static_env = static_env
        self.default_fragments = []
        
        # stack of maps from id to TyExprVar
        self.ty_ids = _util.DictStack([{}])         
        # stack of maps from uniq_id to kind 
        self.ty_vars = _util.DictStack([{}]) 
        # stack of maps from id to uniq_id
        self.exp_ids = _util.DictStack([{}]) 
        # map from uniq_id to ty
        self.exp_vars = _util.DictStack([{}]) 
        self.last_ty_var = 0
        self.last_exp_var = 0

        # map from id to uniq_id
        self.imports = { 'builtins': '__builtins__' }
        self.last_import_var = 0

        # py type for python values
        self.py_type = CanonicalTy(std.py, ())

    #
    # Bindings
    # 

    def push_uty_expr_binding(self, name_ast, k):
        uniq_id = "_ty_" + name_ast.id + "_" + str(self.last_ty_var)
        self.ty_ids[name_ast.id] = TyExprVar(self, name_ast, uniq_id)
        self.ty_vars[uniq_id] = k
        self.last_ty_var += 1

    def push_var_bindings(self, bindings):
        self.exp_ids.push({ })
        self.exp_vars.push({ })
        return self.add_bindings(bindings)

    def pop_var_bindings(self):
        self.exp_ids.pop()
        self.exp_vars.pop()

    def add_binding(self, name_ast, ty):
        return self.add_id_binding(name_ast.id, ty)

    def add_id_binding(self, id, ty):
        uniq_id = "_" + id + "_" + str(self.last_exp_var)
        self.exp_ids[id] = uniq_id
        self.exp_vars[uniq_id] = ty
        self.last_exp_var += 1
        return (uniq_id, ty)

    def add_bindings(self, bindings):
        r = { }
        for (name_ast, ty) in bindings.items():
            uniq_id, ty = self.add_binding(name_ast, ty)
            r[name_ast.id] = (uniq_id, ty)
        return r

    def add_id_var_binding(self, id, var, ty):
        self.exp_ids[id] = var
        self.exp_vars[var] = ty

    def lookup_exp_var_by_id(self, id):
        uniq_id = self.exp_ids[id]
        return uniq_id, self.exp_vars[uniq_id]

    def add_import(self, name):
        imports = self.imports
        if name in imports:
            return imports[name]
        else:
            uniq_id = "_typy_import_" + str(self.last_import_var)
            self.last_import_var += 1
            imports[name] = uniq_id
            return uniq_id

    # 
    # Statements and expressions
    # 

    def check(self, stmt):
        if _terms.is_stmt_expression(stmt):
            return self.syn(stmt)
        elif _terms.is_targeted_stmt_form(stmt):
            target = stmt._typy_target # side effect of the guard call
            form_name = stmt.__class__.__name__
            target_ty = self.syn(target)
            c_target_ty = self.canonicalize(target_ty)
            delegate = stmt.delegate = c_target_ty.fragment
            delegate_idx = stmt.delegate_idx = c_target_ty.idx
            check_method_name = "check_" + form_name
            stmt.translation_method_name = "trans_" + form_name
            check_method = getattr(delegate, check_method_name)
            check_method(self, stmt, delegate_idx)
        elif _terms.is_default_stmt_form(stmt):
            try:
                delegate = stmt.delegate = self.default_fragments[-1]
            except IndexError:
                raise TyError("No default fragment.", stmt)
            delegate_idx = stmt.delegate_idx = None
            cls_name = stmt.__class__.__name__
            check_method_name = "check_" + cls_name
            stmt.translation_method_name = "trans_checked_" + cls_name
            check_method = getattr(delegate, check_method_name)
            check_method(self, stmt)
        elif _terms.is_unsupported_stmt_form(stmt):
            raise TyError("Unsupported statement form.", stmt)
        else:
            raise TyError("Unknown statement form: " + 
                          stmt.__class__.__name__, stmt)

    def ana(self, tree, ty):
        # handle the case where neither left or right synthesize a type
        if isinstance(tree, (ast.BinOp, ast.BoolOp)):
            left, right = _astx.get_left_right(tree)
            try:
                self.syn(left)
            except:
                try:
                    self.syn(right)
                except:
                    ty_c = self.canonicalize(ty)
                    delegate = ty_c.fragment
                    delegate_idx = ty_c.idx

                    # will get picked up by subsumption below
                    class_name = tree.__class__.__name__
                    ana_method = getattr(delegate, "ana_" + class_name)
                    ana_method(self, tree, delegate_idx)
                    tree.ty = ty
                    tree.delegate = delegate
                    tree.delegate_idx = delegate_idx
                    tree.translation_method_name = "trans_" + class_name

        is_intro_form = False
        if _terms.is_intro_form(tree):
            is_intro_form = True
            ty = self.canonicalize(ty)
            classname = tree.__class__.__name__
            ana_method_name = "ana_" + classname
            delegate = ty.fragment
            delegate_idx = ty.idx
            if isinstance(tree, (ast.Name, ast.Call)):
                try:
                    ana_method = getattr(delegate, ana_method_name)
                    ana_method(self, tree, delegate_idx)
                except:
                    delegate = None
                    delegate_idx = None
                else:
                    tree.is_intro_form = True
                    translation_method_name = "trans_" + classname
            else:
                ana_method = getattr(delegate, ana_method_name)
                ana_method(self, tree, delegate_idx)
                tree.is_intro_form = True
                translation_method_name = "trans_" + classname
        if not is_intro_form or (isinstance(tree, (ast.Name, ast.Call)) and delegate is None):
            if isinstance(tree, ast.Expr):
                self.ana(tree.value, ty)
                delegate = delegate_idx = translation_method_name = None
            elif isinstance(tree, _terms.MatchStatementExpression):
                scrutinee = tree.scrutinee
                scrutinee_ty = self.syn(scrutinee)
                scrutinee_ty_c = self.canonicalize(scrutinee_ty)
                delegate = None
                delegate_idx = None
                translation_method_name = None
                for rule in tree.rules:
                    pat = rule.pat
                    bindings = self.ana_pat(rule.pat, scrutinee_ty_c)
                    var_bindings = self.push_var_bindings(bindings)
                    pat.var_bindings = var_bindings
                    block = rule.block = _terms.Block(rule.branch)
                    self.ana_block(block, ty)
                    self.pop_var_bindings()
            elif isinstance(tree, (ast.If, ast.IfExp)):
                test = tree.test
                test_ty = self.syn(test)
                test_ty_c = self.canonicalize(test_ty)
                delegate = test_ty_c.fragment
                delegate_idx = test_ty_c.idx
                class_name = tree.__class__.__name__
                translation_method_name = "trans_" + class_name
                ana_method = getattr(delegate, "ana_" + class_name)
                ana_method(self, tree, delegate_idx, ty)
            else:
                syn_ty = self.syn(tree)
                if self.ty_expr_eq(ty, syn_ty, TypeKind):
                    return
                else:
                    raise TyError(
                        "Type inconsistency. Expected: " + str(self.canonicalize(ty)) + 
                        ". Got: " + str(self.canonicalize(syn_ty)) + ".", tree)

        tree.ty = ty
        tree.delegate = delegate
        tree.delegate_idx = delegate_idx
        tree.translation_method_name = translation_method_name
        if isinstance(tree, ast.FunctionDef):
            try:
                default_fragment = self.default_fragments[-1]
            except IndexError: raise TyError("No default fragment.", stmt)
            tree._default_fragment = default_fragment
            default_fragment.integrate_static_FunctionDef(self, tree)

    def syn(self, tree):
        if hasattr(tree, "ty"): return tree.ty
        if isinstance(tree, ast.Name):
            try:
                uniq_id, ty = self.lookup_exp_var_by_id(tree.id)
                tree.uniq_id = uniq_id
                delegate = None
                delegate_idx = None
                translation_method_name = None
            except KeyError:
                try:
                    static_val = self.static_env[tree.id]
                except KeyError:
                    raise TyError("Invalid name: " + tree.id, tree)
                if isinstance(static_val, _components.Component):
                    delegate = _components.component_singleton
                    ty = CanonicalTy(delegate, static_val)
                    delegate_idx = static_val
                    translation_method_name = "trans_component_ref"
                else:
                    ty = self.py_type
                    delegate = None
                    delegate_idx = None
                    translation_method_name = None
        elif isinstance(tree, ast.Expr):
            ty = self.syn(tree.value)
            delegate = delegate_idx = translation_method_name = None
        elif _terms.is_ascription(tree):
            uty = UTyExpr.parse(tree.ascription)
            ty = self.ana_uty_expr(uty, TypeKind)
            self.ana(tree.value, ty)
            delegate = None
            delegate_idx = None
            translation_method_name = None
        elif _terms.is_targeted_form(tree):
            target = tree._typy_target # side effect of guard call
            form_name = tree.__class__.__name__
            target_ty = self.syn(target)
            can_target_ty = self.canonicalize(target_ty)
            if isinstance(can_target_ty, CanonicalTy):
                delegate = can_target_ty.fragment
                delegate_idx = can_target_ty.idx
                syn_method_name = "syn_" + form_name
                syn_method = getattr(delegate, syn_method_name)
                ty = syn_method(self, tree, delegate_idx)
                translation_method_name = "trans_" + form_name
            else:
                raise TyError(
                    "Target type cannot be canonicalized.", target)
        elif isinstance(tree, ast.FunctionDef):
            decorator_list = tree.decorator_list
            if len(decorator_list) == 0:
                raise TyError(
                    "Cannot synthesize a type for an undecorated " 
                    "definition.",
                    tree)
            asc = decorator_list[0]
            try:
                ty = self.as_type(asc)
            except:
                try:
                    fragment = self.static_env.eval_expr_ast(asc)
                except:
                    raise TyError(
                        "Decorator is neither a type nor a fragment.", 
                        asc)
                else:
                    if not issubclass(fragment, Fragment):
                        raise TyError("First decorator is not a fragment.", asc)
                    self.default_fragments.append(fragment)
                    tree.fragment_ascription = True
                    ty = fragment.syn_FunctionDef(self, tree)
                    self.default_fragments.pop()
                    self.ana_ty_expr(ty, TypeKind)
                    delegate = fragment
                    delegate_idx = ()
                    translation_method_name = "trans_FunctionDef"
            else:
                self.ana(tree, ty) 
                return ty
        elif isinstance(tree, ast.BinOp):
            left = tree.left
            right = tree.right
            delegate, delegate_idx, ty, translation_method_name = \
                self._do_binary(left, right, tree)
        elif isinstance(tree, ast.Compare):
            left = tree.left
            right = tree.comparators[0]
            delegate, delegate_idx, ty, translation_method_name = \
                self._do_binary(left, right, tree)
        elif isinstance(tree, ast.BoolOp): # TODO put these in ast docs order
            left = tree.values[0]
            right = tree.values[1]
            delegate, delegate_idx, ty, translation_method_name = \
                self._do_binary(left, right, tree)
        elif isinstance(tree, _terms.MatchStatementExpression):
            scrutinee = tree.scrutinee
            scrutinee_ty = self.syn(scrutinee)
            scrutinee_ty_c = self.canonicalize(scrutinee_ty)
            delegate = None
            delegate_idx = None
            translation_method_name = None
            ty = None
            for rule in tree.rules:
                pat = rule.pat
                bindings = self.ana_pat(pat, scrutinee_ty_c)
                # print(bindings)
                var_bindings = self.push_var_bindings(bindings)
                # print("var_bindings=", var_bindings)
                pat.var_bindings = var_bindings
                block = rule.block = _terms.Block(rule.branch)
                if ty is None:
                    ty = self.syn_block(block)
                else:
                    self.ana_block(block, ty)
                self.pop_var_bindings()
            if ty is None:
                raise TyError("Cannot synthesize a type for a match statement "
                              "expression without any rules.", tree)
        else:
            raise TyError("Invalid operation: " + tree.__class__.__name__, tree)
        tree.ty = ty
        tree.delegate = delegate
        tree.delegate_idx = delegate_idx
        tree.translation_method_name = translation_method_name
        if isinstance(tree, ast.FunctionDef):
            try:
                default_fragment = self.default_fragments[-1]
            except IndexError: raise TyError("No default fragment.", stmt)
            tree._default_fragment = default_fragment
            default_fragment.integrate_static_FunctionDef(self, tree)
        return ty

    def _do_binary(self, left, right, tree):
        class_name = tree.__class__.__name__
        try:
            left_ty = self.syn(left)
        except:
            left_ty = None
        try:
            right_ty = self.syn(right)
        except:
            right_ty = None
        if left_ty is None and right_ty is None:
            raise TyError(
                "Neither argument synthesizes a type.",
                tree)
        elif left_ty is not None and right_ty is None:
            left_ty_c = self.canonicalize(left_ty)
            delegate = left_ty_c.fragment
            syn_method = getattr(delegate, "syn_" + class_name)
            ty = syn_method(self, tree)
        elif left_ty is None and right_ty is not None:
            right_ty_c = self.canonicalize(right_ty)
            delegate = right_ty_c.fragment
            syn_method = getattr(delegate, "syn_" + class_name)
            ty = syn_method(self, tree)
        else:
            left_ty_c = self.canonicalize(left_ty)
            right_ty_c = self.canonicalize(right_ty)
            left_fragment = left_ty_c.fragment
            right_fragment = right_ty_c.fragment
            if left_fragment is right_fragment:
                delegate = left_fragment
            else:
                left_precedence = left_fragment.precedence
                right_precedence = right_fragment.precedence
                if left_fragment in right_precedence:
                    if right_fragment in left_precedence:
                        raise TyError(
                            "Circular precedence sets.", tree)
                    delegate = right_fragment
                elif right_fragment in left_precedence:
                    delegate = left_fragment
                else:
                    raise TyError(
                        "Left and right of operator synthesize types where "
                        "the fragments are mutually non-precedent.", tree)
            syn_method = getattr(delegate, "syn_" + class_name)
            ty = syn_method(self, tree)
        delegate_idx = None
        translation_method_name = "trans_" + class_name
        return delegate, delegate_idx, ty, translation_method_name

    def ana_block(self, block, ty):
        block.segmented_stmts = segmented_stmts = \
            tuple(self._segment(block.stmts))
        if len(segmented_stmts) == 0:
            raise TyError("Empty block", None)

        for stmt in segmented_stmts[:-1]: # all but last
            self.check(stmt)

        last_stmt = segmented_stmts[-1]
        self.ana(last_stmt, ty)

    def syn_block(self, block):
        block.segmented_stmts = segmented_stmts = \
            tuple(self._segment(block.stmts))
        if len(segmented_stmts) == 0:
            raise TyError("Empty block", None)

        for stmt in segmented_stmts[:-1]: # all but last
            self.check(stmt)

        last_stmt = segmented_stmts[-1] # TODO insert error check for if its not a stmt expression
        return self.syn(last_stmt)

    def trans_block(self, block, mechanism):
        translation = [ ]
        segmented_stmts = block.segmented_stmts
        if mechanism == BlockTransMechanism.Statement:
            for stmt in segmented_stmts:
                translation.extend(self.trans(stmt))
        else:
            all_but_last = segmented_stmts[:-1]
            last = segmented_stmts[-1]
            for stmt in all_but_last:
                translation.extend(self.trans(stmt))
            translation.extend(self.trans(last, mechanism))
        return translation

    @staticmethod
    def _segment(stmts):
        cur_scrutinizer = None
        cur_rules = None
        for stmt in stmts:
            if cur_scrutinizer is not None:
                if isinstance(stmt, ast.With):
                    rule = _terms.MatchRule.parse_with_stmt(stmt)
                    cur_rules.append(rule)
                    continue
                else:
                    yield _terms.MatchStatementExpression(
                        cur_scrutinizer,
                        cur_rules)
                    cur_scrutinizer = None
                    cur_rules = None

            if _terms.is_match_scrutinizer(stmt):
                cur_scrutinizer = stmt
                cur_rules = [ ]
                continue
            else:
                yield stmt

        if cur_scrutinizer is not None:
            yield _terms.MatchStatementExpression(
                cur_scrutinizer,
                cur_rules)

    def trans(self, tree, mechanism=BlockTransMechanism.Statement):
        if hasattr(tree, 'delegate') and tree.delegate is not None:
            delegate = tree.delegate
            idx = tree.delegate_idx
            translation_method_name = tree.translation_method_name
            if translation_method_name is None:
                raise TyError("missing translation method", tree)
            translation_method = getattr(delegate, translation_method_name)
            if idx is not None:
                if _terms.is_stmt_expression(tree):
                    translation = translation_method(self, tree, idx, mechanism)
                else:
                    translation = translation_method(self, tree, idx)
            else:
                if _terms.is_stmt_expression(tree):
                    translation = translation_method(self, tree, mechanism)
                else:
                    translation = translation_method(self, tree)
        elif isinstance(tree, ast.Name):
            if hasattr(tree, "uniq_id"):
                uniq_id = tree.uniq_id
                translation = ast.copy_location(
                    ast.Name(id=uniq_id, ctx=tree.ctx),
                    tree)
            else:
                translation = ast.copy_location(
                    ast.Name(id=tree.id, ctx=tree.ctx), 
                    tree)
        elif _terms.is_ascription(tree):
            translation = self.trans(tree.value)
        elif isinstance(tree, ast.Expr):
            value_tr = self.trans(tree.value)
            if mechanism == BlockTransMechanism.Statement:
                translation = [
                    ast.copy_location(
                        ast.Expr(value=value_tr),
                        tree)]
            elif mechanism == BlockTransMechanism.Return:
                translation = [
                    ast.copy_location(
                        ast.Return(value=value_tr),
                        tree)]
        elif isinstance(tree, _terms.MatchStatementExpression):
            # __typy__scrutinee__ = scrutinee_trans
            # if condition1:
            #     binding1 = value1
            #     binding2 = value2
            #     binding3 = value3
            #     ...
            #     branch translation
            # elif condition2: ...
            # ...
            # else:
            #     raise Exception('typy match failure')
            scrutinee = tree.scrutinee
            scrutinee_trans = self.trans(scrutinee)
            scrutinee_var = ast.copy_location(
                ast.Name(id="__typy_scrutinee__", ctx=_astx.load_ctx),
                scrutinee)
            scrutinee_var_store = ast.copy_location(
                ast.Name(id="__typy_scrutinee__", ctx=_astx.store_ctx), 
                scrutinee)
            rules = tree.rules
            rule_stmts = [ ]
            conditions = [ ]
            branches = [ ]
            for rule in rules:
                rule_stmts.append(rule.stmt)
                pat = rule.pat
                condition, binding_translations = self.trans_pat(pat, scrutinee_var)
                conditions.append(condition)
                branch = _astx.assignments_from_dict(
                    dict(
                        (uniq_id, (binding_translations[id], pat))
                        for id, (uniq_id, _) in pat.var_bindings.items()
                    )
                )
                branch.extend(self.trans_block(rule.block, mechanism))
                branches.append(branch)

            translation = [
                ast.copy_location(
                    ast.Assign(targets=[scrutinee_var_store], value=scrutinee_trans),
                    scrutinee)
            ]
            translation.extend(_astx.conditionals(
                conditions, branches, rule_stmts, 
                [_astx.standard_raise_str('Exception', 
                                         'typy match failure', scrutinee)]))
        else:
            print(tree.__class__.__name__)
            raise NotImplementedError()

        if isinstance(tree, ast.FunctionDef):
            default_fragment = tree._default_fragment
            default_fragment.integrate_trans_FunctionDef(self, tree, translation, mechanism)
        tree.translation = translation
        return translation

    # def trans_FunctionDef(self, stmt, id):
    #     if isinstance(stmt, ast.FunctionDef):
    #         delegate = stmt.delegate
    #         translation = stmt.translation = delegate.trans_FunctionDef(self, stmt, id)
    #         return translation
    #     else:
    #         raise NotImplementedError()

    # 
    # Patterns
    # 

    def ana_pat(self, pat, ty):
        if isinstance(pat, ast.Name) and not _terms.is_intro_form(pat):
            id = pat.id
            if id == "_":
                return { }
            else:
                return { pat: ty }
        else:
            canonical_ty = self.canonicalize(ty)
            delegate = pat.delegate = canonical_ty.fragment
            delegate_idx = pat.delegate_idx = canonical_ty.idx
            method_name = "ana_pat_" + pat.__class__.__name__
            method = getattr(delegate, method_name)
            bindings = method(self, pat, delegate_idx)
            pat.bindings = bindings
            return bindings

    def trans_pat(self, pat, scrutinee_trans):
        if isinstance(pat, ast.Name) and not _terms.is_intro_form(pat):
            id = pat.id
            if id == "_":
                binding_translations = { }
            else:
                binding_translations = { id : scrutinee_trans }
            condition = ast.copy_location(
                ast.NameConstant(value=True), pat) 
            return condition, binding_translations
        else:
            delegate = pat.delegate
            delegate_idx = pat.delegate_idx
            method_name = "trans_pat_" + pat.__class__.__name__ # TODO add stubs
            method = getattr(delegate, method_name)
            return method(self, pat, delegate_idx, scrutinee_trans)

    # 
    # Kinds and type expressions
    # 

    def is_kind(self, k):
        if k == TypeKind: return True
        elif isinstance(k, SingletonKind):
            self.ana(k.ty, TypeKind)
            return True
        else:
            raise UsageError("Invalid kind")
    
    def kind_eq(self, k1, k2):
        if k1 is k2:
            return True
        elif (isinstance(k1, SingletonKind) 
              and isinstance(k2, SingletonKind)):
            return self.ty_expr_eq(k1.ty, k2.ty, TypeKind)
        else:
            return False

    def subkind(self, k1, k2):
        if self.kind_eq(k1, k2): 
            return True
        elif isinstance(k1, SingletonKind) and k2 == TypeKind:
            return True
        else:
            return False

    def syn_ty_expr(self, c):
        if isinstance(c, TyExprVar):
            uniq_id = c.uniq_id
            try:
                return self.ty_vars[uniq_id]
            except KeyError:
                raise KindError(
                    "Unbound type variable: " + c.name_ast.id,
                    c)
        elif isinstance(c, CanonicalTy):
            return SingletonKind(c)
        elif isinstance(c, TyExprPrj):
            path_val = c.path_val
            lbl = c.lbl
            return path_val.kind_of(lbl)
        else:
            raise UsageError("Invalid construction.")

    def ana_ty_expr(self, c, k):
        syn_k = self.syn_ty_expr(c)
        if self.subkind(syn_k, k): return
        else:
            raise KindError(
                "Kind mismatch. Expected: '" + str(k) + 
                "'. Got: '" + str(syn_k) + "'.",
                c)

    def ty_expr_eq(self, c1, c2, k):
        if c1 == c2:
            self.ana_ty_expr(c1, k) 
            return True
        elif k == TypeKind:
            if isinstance(c1, CanonicalTy):
                if isinstance(c2, CanonicalTy):
                    return (c1.fragment == c2.fragment 
                            and c1.fragment.idx_eq(self, c1.idx, c2.idx))
                else:
                    return self.ty_expr_eq(c1, self.canonicalize(c2), k)
            else:
                return self.ty_expr_eq(self.canonicalize(c1), c2, k)
        elif isinstance(k, SingletonKind):
            try:
                return self.ana_ty_expr(c1, k) and self.ana_ty_expr(c2, k)
            except KindError:
                return False
        else:
            raise KindError("Invalid kind.", k)

    def canonicalize(self, ty):
        if isinstance(ty, CanonicalTy): return ty
        elif isinstance(ty, TyExprVar) or isinstance(ty, TyExprPrj):
            k = self.syn_ty_expr(ty)
            if k == TypeKind:
                return ty
            elif isinstance(k, SingletonKind):
                return self.canonicalize(k.ty)
            else:
                raise UsageError("Invalid kind.")
        else:
            print(ty)
            raise UsageError("Invalid construction.")

    def ana_uty_expr(self, uty_expr, k):
        if isinstance(uty_expr, UName):
            id = uty_expr.id
            static_env = self.static_env
            ty_ids = self.ty_ids
            if id in ty_ids:
                convar = ty_ids[id]
                self.ana_ty_expr(convar, k)
                return convar
            elif id in static_env:
                static_val = self.static_env[id]
                if is_fragment(static_val):
                    ty = CanonicalTy.new(self, static_val, 
                                         ast.Index(
                                             value=_astx.empty_tuple_ast))
                    self.ana_ty_expr(ty, k)
                    return ty
                else:
                    raise KindError(
                        "Type expression '" + 
                        id + 
                        "' is bound to static value '" + 
                        repr(static_val) + 
                        "', which is neither a fragment nor a " +
                        "type expression.", uty_expr)
            else:
                raise KindError(
                    "Type expression '" + 
                    id + 
                    "' is unbound.", uty_expr)
        elif isinstance(uty_expr, UCanonicalTy):
            fragment_ast = uty_expr.fragment_ast
            idx_ast = uty_expr.idx_ast
            static_env = self.static_env
            fragment = static_env.eval_expr_ast(fragment_ast)
            if is_fragment(fragment):
                ty = CanonicalTy.new(self, fragment, idx_ast)
                self.ana_ty_expr(ty, k)
                return ty
            else:
                raise KindError(
                    "Term did not evaluate to a fragment in "
                    "static environment.",
                    fragment_ast)
        elif isinstance(uty_expr, UProjection):
            path_ast, lbl = uty_expr.path_ast, uty_expr.lbl
            path_val = self.static_env.eval_expr_ast(path_ast)
            if _components.is_component(path_val):
                con = TyExprPrj(path_ast, path_val, lbl)
                self.ana_ty_expr(con, k)
                return con
            else:
                try:
                    fragment = getattr(path_val, lbl)
                except AttributeError:
                    raise KindError(
                        "Invalid projection.", path_ast)
                else:
                    if is_fragment(fragment):
                        ty = CanonicalTy.new(self, fragment, 
                                             ast.Index(
                                                 value=_astx.empty_tuple_ast))
                        self.ana_ty_expr(ty, k)
                        return ty
                    else:
                        raise KindError(
                            "Invalid projection.", path_ast)
        else:
            raise KindError(
                "Invalid type expression: " + repr(uty_expr), uty_expr)

    def as_type(self, expr):
        uty_expr = UTyExpr.parse(expr)
        return self.ana_uty_expr(uty_expr, TypeKind)

