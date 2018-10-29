"""typy component system"""

import ast
import inspect
import textwrap

import astunparse

from .util import astx as _astx
from ._errors import ComponentFormationError, InternalError
from ._fragments import Fragment
from ._static_envs import StaticEnv
from ._contexts import Context, BlockTransMechanism
from ._ty_exprs import UTyExpr, UName, TypeKind, SingletonKind
from . import _terms

__all__ = ('component', 'Component', 'is_component')

def component(f):
    """Decorator that transforms Python function definitions into Components."""
    (tree, static_env) = _reflect_func(f)
    c = Component(tree, static_env)
    c._evaluate()
    return c

def _reflect_func(f):
    """Returns the ast and StaticEnv of Python function f."""
    source = textwrap.dedent(inspect.getsource(f))
    tree = ast.parse(source).body[0]
    static_env = StaticEnv.from_func(f)
    return (tree, static_env)

class Component(object):
    """Top-level components."""
    def __init__(self, tree, static_env):
        """Called by component."""
        self.tree = tree
        self.static_env = static_env
        self._parsed = False
        self._checked = False
        self._translated = False
        self._evaluated = False

    def _parse(self):
        if self._parsed: return

        tree = self.tree

        # make sure there are no arguments
        if not _astx.is_empty_args(tree.args):
            raise ComponentFormationError(
                "Components cannot take arguments.", tree)

        # parse the members
        def _parse_members():
            body = list(tree.body)
            while len(body) > 0:
                stmt = body.pop(0)
                if isinstance(stmt, ast.Assign):
                    type_member = TypeMember.parse_Assign(stmt)
                    if type_member is not None: yield type_member
                    else:
                        value_member = ValueMember.parse_Assign(stmt)
                        if value_member is not None: yield value_member
                        else: 
                            raise ComponentFormationError(
                                "Invalid member definition.", stmt)
                elif isinstance(stmt, ast.FunctionDef):
                    value_member = ValueMember.parse_FunctionDef(stmt)
                    if value_member is not None: yield value_member
                    else:
                        raise ComponentFormationError(
                            "Invalid member definition.", stmt)
                else:
                    stmt_member = StmtMember.parse_stmts(stmt, body)
                    if stmt_member is not None: yield stmt_member
                    else:
                        raise ComponentFormationError(
                            "Invalid statement form in component definition.", stmt)
        members = self._members = tuple(_parse_members())

        # determine exports
        ty_expr_exports = self._ty_expr_exports = { }
        val_exports = self._val_exports = { }
        for member in members:
            if isinstance(member, TypeMember):
                exports = ty_expr_exports
            elif isinstance(member, ValueMember):
                exports = val_exports
            else:
                continue
            lbl = member.id
            if lbl in exports:
                raise ComponentFormationError(
                    "Duplicate component member: " + lbl, member.tree)
            exports[lbl] = member

        self._parsed = True

    def _check(self):
        if self._checked: return
        self._parse()
        ctx = self.ctx = Context(self.static_env)
        ctx.default_fragments.append(component_singleton)
        for member in self._members:
            try:
                print("checking " + member.id)
            except: pass
            member.check(ctx)
        self._checked = True

    def _translate(self):
        if self._translated: return
        self._check()
        _members = self._members
        body = [ ]
        for member in self._members:
            translation = member.translate(self.ctx)
            body.extend(translation)
        imports = self.ctx.imports
        for name in sorted(imports.keys()):
            asname = imports[name]
            body.insert(0, 
                ast.Import(names=[ast.alias(name=name, asname=asname)],
                           lineno=0, col_offset=0))
        self._translation = ast.Module(
            body=body,
            lineno=0, col_offset=0) # TODO
        self._translated = True

    def _evaluate(self):
        if self._evaluated: return
        self._translate()
        _translation = self._translation
        try:
            self._module = self.static_env.eval_module_ast(_translation)
        except Exception as e:
            print("Broken code: ", astunparse.unparse(_translation))
            raise e
        self._evaluated = True

    def kind_of(self, lbl):
        exports = self._ty_expr_exports
        if lbl in exports:
            member = exports[lbl]
            if isinstance(member, TypeMember):
                return member.kind

def is_component(x):
    return isinstance(x, Component)

class ComponentMember(object):
    """Base class for component members."""

class TypeMember(ComponentMember):
    """Type members."""
    def __init__(self, id, name_ast, uty_expr, tree):
        self.id = id
        self.name_ast = name_ast
        self.uty_expr = uty_expr
        self.tree = tree

    @classmethod
    def parse_Assign(cls, stmt):
        targets, value = stmt.targets, stmt.value
        if len(targets) != 1:
            raise ComponentFormationError(
                "Too many assignment targets.", stmt)
        target = targets[0]
        if isinstance(target, ast.Subscript):
            target_value = target.value
            if isinstance(target_value, ast.Name):
                slice = target.slice
                if isinstance(slice, ast.Index):
                    slice_value = slice.value
                    if isinstance(slice_value, ast.Name):
                        if slice_value.id == "type":
                            uty_expr = UTyExpr.parse(value)
                            return cls(target_value.id, 
                                       target_value, uty_expr, stmt)

    def check(self, ctx):
        ty = self.ty = ctx.ana_uty_expr(self.uty_expr, TypeKind)
        kind = self.kind = SingletonKind(ctx.canonicalize(ty))
        ctx.push_uty_expr_binding(self.name_ast, kind)

    def translate(self, ctx): 
        return []

class ValueMember(ComponentMember):
    """Value members."""
    def __init__(self, id, uty, tree):
        self.id = id
        self.uty = uty
        self.tree = tree

    @classmethod
    def parse_Assign(cls, stmt):
        targets, value = stmt.targets, stmt.value
        if len(targets) != 1:
            raise ComponentFormationError(
                "Too many assignment targets.", stmt)
        target = targets[0]
        if isinstance(target, ast.Subscript):
            target_value = target.value
            if isinstance(target_value, ast.Name):
                slice = target.slice
                if isinstance(slice, ast.Slice):
                    lower, upper, step = slice.lower, slice.upper, slice.step
                    if lower is None and upper is not None and step is None:
                        uty = UTyExpr.parse(upper)
                        
                        return cls(target_value.id, uty, stmt)
        elif isinstance(target, ast.Name):
            return cls(target.id, None, stmt)

    @classmethod
    def parse_FunctionDef(cls, stmt):
        return cls(stmt.name, None, stmt)

    def check(self, ctx):
        tree = self.tree
        if isinstance(tree, ast.Assign):
            tree_ = tree.value
        elif isinstance(tree, ast.FunctionDef):
            tree_ = tree
        else: raise InternalError("Invalid form.")

        uty = self.uty
        if uty is None:
            ty = ctx.syn(tree_)
        else:
            ty = ctx.ana_uty_expr(uty, TypeKind)
            ctx.ana(tree_, ty)

        ctx.add_id_var_binding(self.id, self.id, ty)
        self.ty = ctx.canonicalize(ty)

    def translate(self, ctx):
        tree = self.tree
        if isinstance(tree, ast.Assign):
            target = ast.copy_location(ast.Name(id=self.id, ctx=ast.Store()), tree)
            assignment = ast.copy_location(ast.Assign(
                targets=[target],
                value=ctx.trans(tree.value)), tree)
            translation = self.translation = (assignment,)
            return translation
        elif isinstance(tree, ast.FunctionDef):
            return ctx.trans(tree)

class StmtMember(ComponentMember):
    """Statement members (not exported)."""
    def __init__(self, stmt):
        self.stmt = stmt

    @classmethod
    def parse_stmts(cls, stmt, body):
        if _terms.is_match_scrutinizer(stmt):
            rules = [ ] 
            while len(body) > 0:
                next_stmt = body[0]
                if _terms.is_match_rule(next_stmt):
                    body.pop(0)
                    rules.append(_terms.MatchRule.parse_with_stmt(next_stmt))
                else:
                    break
            return cls(_terms.MatchStatementExpression(stmt, rules))
        elif _terms.is_supported_stmt_form(stmt):
            if not isinstance(stmt, (ast.Return, ast.Delete)):
                return cls(stmt)

    def check(self, ctx):
        ctx.check(self.stmt)

    def translate(self, ctx):
        return ctx.trans(self.stmt)

class component_singleton(Fragment):
    @classmethod
    def syn_Attribute(cls, ctx, e, idx):
        try:
            member = idx._val_exports[e.attr]
        except KeyError:
            raise TyError("Invalid component member: " + e.attr, e)
        if isinstance(member, ValueMember):
            return member.ty
        else:
            raise TyError("Component member is not a value member: " + e.attr, e)

    @classmethod
    def trans_Attribute(cls, ctx, e, idx):
        return ast.fix_missing_locations(ast.copy_location(
            ast.Attribute(
                value=ctx.trans(e.value),
                attr=e.attr,
                ctx=ast.Load()),
            e))

    @classmethod
    def integrate_static_FunctionDef(cls, ctx, stmt):
        stmt.uniq_id = stmt.name

    @classmethod
    def integrate_trans_FunctionDef(cls, ctx, stmt, translation, mechanism):
        pass

    @classmethod
    def trans_component_ref(cls, ctx, e, idx):
        return ast.fix_missing_locations(ast.copy_location(
            ast.Attribute(
                value=e,
                attr="_module",
                ctx=_astx.load_ctx),
            e))
        
    @classmethod
    def check_Pass(cls, ctx, stmt):
        return

    @classmethod
    def trans_checked_Pass(cls, ctx, stmt):
        return [_astx.copy_node(stmt)]

    @classmethod
    def check_Expr(cls, ctx, stmt):
        ctx.syn(stmt.value)

    @classmethod
    def trans_checked_Expr(cls, ctx, stmt, mechanism):
        if mechanism == BlockTransMechanism.Statement:
            return [ast.copy_location(
                ast.Expr(value=ctx.trans(stmt.value)),
                stmt)]
        else:
            raise TyError("Invalid mechanism.", stmt)

