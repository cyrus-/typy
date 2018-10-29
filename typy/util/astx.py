"""Utilities for working with python's standard ast library"""
import ast 
import re

def copy_node(node, *args, **kwargs):
    """Shallow copies the provided ast node.

    Non-keyword arguments are set according to the order in the Python ast documentation.
    Keyword arguments are set explicitly.
    """
    cls = node.__class__
    new_node = cls()

    set_attrs = {}

    # non-keyword args
    for name, value in zip(cls._fields, args):
        set_attrs[name] = value

    # keyword args
    for name, value in kwargs.items():
        set_attrs[name] = value

    # attributes
    for name, value in node.__dict__.items():
        if name not in set_attrs:
            set_attrs[name] = value

    # apply set_attrs
    for name, value in set_attrs.items():
        setattr(new_node, name, value)

    return new_node

def deep_copy_node(node, *args, **kwargs):
    """Deep copies the provided ast node.

    Non-keyword arguments are set according to the order in the Python ast documentation.

    Keyword arguments are set explicitly."""
    cls = node.__class__
    new_node = cls()

    set_attrs = {}

    # non-keyword args
    for name, value in zip(cls._fields, args):
        set_attrs[name] = value

    # keyword args
    for name, value in kwargs.items():
        set_attrs[name] = value

    # deep copy attributes
    for name, value in node.__dict__.items():
        if name not in set_attrs:
            if isinstance(value, ast.AST):
                set_attrs[name] = deep_copy_node(value)
            else:
                set_attrs[name] = value

    # apply set_attrs
    for name, value in set_attrs.items():
        setattr(new_node, name, value)

    return new_node

empty_tuple_ast = ast.Tuple(elts=[])
load_ctx = ast.Load()
store_ctx = ast.Store()

def import_expr(name):
    return builtin_call('__import__', [ast.Str(s=name)])

def method_call(obj, method_name, args):
    return ast.Call(
        func=ast.Attribute(
            value=obj,
            attr=method_name,
            ctx=load_ctx),
        args=args,
        keywords=[],
        starargs=None,
        kwargs=None)

_name_re = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*$")
def is_identifier(id):
    return bool(_name_re.match(id))

def _get_arg_names(args):
    return tuple(arg.id for arg in args.args)

def make_Lambda(arg_vars, body):
    return ast.Lambda(
        args=ast.arguments(
            args=[
                ast.Name(id=arg_var, ctx=ast.Param())
                for arg_var in arg_vars],
            vararg=None,
            kwarg=None,
            defaults=[]),
        body=body)

def make_simple_Call(func, args):
    return ast.Call(
        func=func,
        args=args,
        keywords=[],
        starargs=None,
        kwargs=None)

def expr_Raise_Exception_string(message):
    # hack: (_ for _ in ()).throw(Exception(message))
    return ast.Call(
        func=ast.Attribute(
            value=ast.GeneratorExp(
                elt=ast.Name(id='_', ctx=load_ctx),
                generators=[
                    ast.comprehension(
                        target=ast.Name(id='_', ctx=ast.Store()),
                        iter=ast.Tuple(
                            elts=[], 
                            ctx=load_ctx), 
                        ifs=[])]), 
            attr='throw', ctx=load_ctx),
        args=[builtin_call('Exception', [ast.Str(s=message)])],
        keywords=[],
        starargs=None,
        kwargs=None)

def stmt_Raise_Exception_string(message):
    return ast.Raise(
        type=builtin_call('Exception', [ast.Str(s=message)]),
        inst=None, 
        tback=None)

def make_binary_And(left, right):
    return ast.BoolOp(
        op=ast.And(),
        values=[left, right])

def make_Attribute(value, attr):
    return ast.Attribute(
        value=value,
        attr=attr,
        ctx=load_ctx)

def make_Subscript_Num_Index(value, n):
    return ast.Subscript(
        value=value,
        slice=ast.Index(
            value=ast.Num(n=n)
        ),
        ctx=load_ctx)

def cond_vacuously_true(cond):
    if isinstance(cond, ast.Name) and cond.id == "True":
        return True
    if isinstance(cond, ast.BoolOp):
        if isinstance(cond.op, ast.And):
            for value in cond.values:
                if not cond_vacuously_true(value):
                    return False
            return True
    return False

def is_empty_args(args):
    return (len(args.args) == 0 and 
            args.vararg is None and 
            len(args.kwonlyargs) == 0 and 
            args.kwarg is None)

def assignments_from_dict(d):
    r = [ ]
    for id, (value, loc_source) in d.items():
        r.append(ast.fix_missing_locations(ast.copy_location(
            ast.Assign(
                targets=[ast.Name(id=id, ctx=store_ctx)],
                value=value), loc_source)))
    return r

def conditionals(conditions, branches, loc_sources, orelse):
    n_conditions = len(conditions)
    if n_conditions == 0:
        return orelse
    elif n_conditions == 1:
        return [ast.copy_location(ast.If(
            test=conditions[0],
            body=branches[0],
            orelse=orelse), loc_sources[0])]
    else:
        return [ast.copy_location(ast.If(
            test=conditions[0],
            body=branches[0],
            orelse=conditionals(
                conditions[1:],
                branches[1:],
                loc_sources[1:],
                orelse)), loc_sources[0])]

def standard_raise_str(exn, s, loc_source):
    return ast.fix_missing_locations(ast.copy_location(ast.Raise(
        exc=ast.Call(
            func=ast.Name(id=exn, ctx=load_ctx),
            args=[
                ast.Str(s=s)
            ],
            keywords=[]),
        cause=None), loc_source))

def get_left_right(e):
    if isinstance(e, ast.BoolOp):
        return e.values[0], e.values[1]
    elif isinstance(e, ast.BinOp):
        return e.left, e.right
    elif isinstance(e, ast.Compare):
        return e.left, e.comparators[0]

def builtin_call(id, args):
    return ast.Call(
        func=ast.Attribute(
            value=ast.Name(id="__builtins__", ctx=load_ctx),
            attr=id,
            ctx=load_ctx
        ),
        args=args,
        keywords=[])

def isinstance_builtin_id(scrutinee, cls_name):
    return builtin_call('isinstance', [
                scrutinee,
                ast.Attribute(
                    value=ast.Name(id="__builtins__", ctx=load_ctx),
                    attr=cls_name,
                    ctx=load_ctx)])

def is_underscore(e):
    return isinstance(e, ast.Name) and e.id == "_"


