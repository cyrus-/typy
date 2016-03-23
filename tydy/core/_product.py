"""typy product types"""
import ast 

import six

import typy
import typy.util as _util
import typy.util.astx as astx

import _boolean

#
# tpl
#

class tpl(typy.Type):
    @classmethod
    def init_idx(cls, idx):
        return _util.odict(_normalize_tuple_idx(idx)) 

    @classmethod
    def init_inc_idx(cls, inc_idx):
        if inc_idx == Ellipsis:
            return inc_idx
        else:
            raise typy.TypeFormationError(
                "Incomplete tuple type must have Ellipsis index.")

    def anon_to_str(self):
        idx = self.idx
        return (
            "tpl[" + 
            (str.join(", ", self._idx_to_str())
             if len(idx) > 0 
             else "()") + 
            "]"
        )

    def _idx_to_str(self):
        idx = self.idx
        str_label_seen = False
        for i, (label, ty) in enumerate(idx.iteritems()):
            if i == label:
                if not str_label_seen:
                    yield str(ty)
                    continue
            else:
                str_label_seen = True
            yield repr(label) + " : " + str(ty)

    def ana_Tuple(self, ctx, e):
        elts = e.elts
        idx = self.idx

        n_elts, n_idx = len(elts), len(idx)
        if n_elts < n_idx:
            raise typy.TypeError(
                "Too few components provided.", e)
        elif n_elts > n_idx:
            raise typy.TypeError(
                "Too many components provided.", elts[n_idx])

        for elt, ty in zip(elts, idx.itervalues()):
            ctx.ana(elt, ty)

    @classmethod
    def syn_idx_Tuple(cls, ctx, e, inc_idx):
        return tuple(_syn_idx_Tuple(cls, ctx, e.elts))

    def translate_Tuple(self, ctx, e):
        translation = astx.copy_node(e)
        translation.elts = tuple(
            ctx.translate(elt)
            for elt in e.elts)
        return translation 

    def ana_pat_Tuple(self, ctx, pat):
        elts = pat.elts
        idx = self.idx
        n_elts, n_idx = len(elts), len(idx)
        if n_elts < n_idx:
            raise typy.TypeError(
                "Too few components in tpl pattern.", pat)
        elif n_elts > n_idx:
            raise typy.TypeError(
                "Too many components in tpl pattern.", elts[n_idx])
        
        bindings = _util.odict()
        n_bindings = 0
        for elt, ty in zip(elts, idx.itervalues()):
            elt_bindings = ctx.ana_pat(elt, ty)
            n_elt_bindings = len(elt_bindings)
            bindings.update(elt_bindings)
            n_bindings_new = len(bindings)
            if n_bindings_new != n_bindings + n_elt_bindings:
                raise typy.TypeError("Duplicate variable in pattern.", pat)
            n_bindings = n_bindings_new
        
        return bindings

    def translate_pat_Tuple(self, ctx, pat, scrutinee_trans):
        scrutinee_trans_copy = astx.copy_node(scrutinee_trans)
        elts = pat.elts
        idx = self.idx
        conditions = []
        binding_translations = _util.odict()
        for n, (elt, ty) in enumerate(zip(elts, idx.itervalues())):
            elt_scrutinee_trans = astx.make_Subscript_Num_Index(
                scrutinee_trans_copy,
                n)
            elt_condition, elt_binding_translations = ctx.translate_pat(
                elt, elt_scrutinee_trans)
            conditions.append(elt_condition)
            binding_translations.update(elt_binding_translations)
        condition = ast.BoolOp(
            op=ast.And(),
            values=conditions)
        return (condition, binding_translations)

    def ana_Dict(self, ctx, e):
        keys, values = e.keys, e.values
        idx = self.idx
        n_keys, n_idx = len(keys), len(idx)
        if n_keys < n_idx:
            raise typy.TypeError(
                "Too few components provided.", e)
        elif n_keys > n_idx:
            raise typy.TypeError(
                "Too many components provided.", e)

        used_labels = set()
        for key, value in zip(keys, values):
            label = _read_label(key)
            if label in used_labels:
                raise typy.TypeError(
                    "Duplicate label: " + str(label), key)
            try:
                ty = idx[label]
            except KeyError:
                raise typy.TypeError(
                    "Invalid label: " + str(label), key)
            used_labels.add(label)
            key.label = label
            ctx.ana(value, ty)

    @classmethod
    def syn_idx_Dict(cls, ctx, e, inc_idx):
        return tuple(_syn_idx_Dict(cls, ctx, e.keys, e.values))

    def translate_Dict(self, ctx, e):
        keys, values = e.keys, e.values
        idx = self.idx
        elt_translation = []
        idx_mapping = []
        for key, value in zip(keys, values):
            label = key.label
            elt_translation.append(ctx.translate(value))
            i = _util.odict_idx_of(idx, label)
            idx_mapping.append(i)
        arg_translation = ast.Tuple(elts=elt_translation)

        return ast.copy_location(
            _labeled_translation(idx_mapping, arg_translation), 
            e)

    def ana_pat_Dict(self, ctx, pat):
        keys, values = pat.keys, pat.values
        idx = self.idx
        n_keys, n_idx = len(keys), len(idx)
        if n_keys < n_idx:
            raise typy.TypeError("Too few elements in pattern.", pat)
        elif n_keys > n_idx:
            raise typy.TypeError("Too many elements in pattern.", keys[n_idx])

        used_labels = set()
        bindings = _util.odict()
        n_bindings = 0 
        for key, value in zip(keys, values):
            label = _read_label(key)
            if label in used_labels:
                raise typy.TypeError("Duplicate label: " + str(label), key)
            used_labels.add(label)
            key.label = label

            try:
                ty = idx[label]
            except KeyError:
                raise typy.TypeError("Invalid label: " + str(label), key)
            elt_bindings = ctx.ana_pat(value, ty)
            n_elt_bindings = len(elt_bindings)
            bindings.update(elt_bindings)
            n_bindings_new = len(bindings)
            if n_bindings_new != n_bindings + n_elt_bindings:
                raise typy.TypeError("Duplicate variable in pattern.", pat)
            n_bindings = n_bindings_new

        return bindings

    def translate_pat_Dict(self, ctx, pat, scrutinee_trans):
        scrutinee_trans_copy = astx.copy_node(scrutinee_trans)
        keys, values = pat.keys, pat.values
        idx = self.idx
        conditions = []
        binding_translations = _util.odict()
        for key, value in zip(keys, values):
            label = key.label
            n = _util.odict_idx_of(idx, label)
            elt_scrutinee_trans = astx.make_Subscript_Num_Index(
                scrutinee_trans_copy,
                n)
            elt_condition, elt_binding_translations = ctx.translate_pat(
                value, elt_scrutinee_trans)
            conditions.append(elt_condition)
            binding_translations.update(elt_binding_translations)
        condition = ast.BoolOp(
            op=ast.And(),
            values=conditions)
        return (condition, binding_translations)

    def ana_Call_constructor(self, ctx, e):
        id = e.func.id
        if id != 'X':
            raise typy.TypeError("tpl only supports the X constructor")
        if e.starargs is not None:
            raise typy.TypeError("No support for starargs", e)
        if e.kwargs is not None:
            raise typy.TypeError("No support for kwargs", e)

        idx = self.idx
        args = e.args
        keywords = e.keywords

        # check counts
        n_idx = len(idx)
        n_args, n_keywords = len(args), len(keywords)
        n_elts = n_args + n_keywords
        if n_elts < n_idx:
            raise typy.TypeError("Too few elements.", e)
        elif n_elts > n_idx:
            raise typy.TypeError("Too many elements.", e)

        # process non-keywords
        for i, arg in enumerate(args):
            try:
                ty = idx[i]
            except KeyError:
                raise typy.TypeError("No component labeled " + str(i), arg)
            ctx.ana(arg, ty)

        # process keywords
        for keyword in keywords:
            label = keyword.arg
            try:
                ty = idx[label]
            except KeyError:
                raise typy.TypeError("No component labeled " + label, label)
            value = keyword.value
            ctx.ana(value, ty)

    @classmethod
    def syn_idx_Call_constructor(self, ctx, e, inc_idx):
        return tuple(_syn_idx_Call_constructor(ctx, e))

    def translate_Call_constructor(self, ctx, e):
        args, keywords = e.args, e.keywords
        idx = self.idx

        elt_translation = []
        idx_mapping = []
        for i, arg in enumerate(args):
            elt_translation.append(ctx.translate(arg))
            n = _util.odict_idx_of(idx, i)
            idx_mapping.append(n)
        for keyword in keywords:
            label = keyword.arg
            value = keyword.value
            elt_translation.append(ctx.translate(value))
            n = _util.odict_idx_of(idx, label)
            idx_mapping.append(n)
        arg_translation = ast.Tuple(elts=elt_translation)

        return ast.copy_location(_labeled_translation(idx_mapping, 
                                                      arg_translation), 
                                 e)

    def ana_pat_Call_constructor(self, ctx, pat):
        id = pat.func.id
        if id != 'X':
            raise typy.TypeError("tpl supports only the 'X' constructor", pat.func)
        if pat.starargs is not None:
            raise typy.TypeError("No support for starargs", pat)
        if pat.kwargs is not None:
            raise typy.TypeError("No support for kwargs", pat)

        args = pat.args
        keywords = pat.keywords
        idx = self.idx

        bindings = _util.odict()
        n_bindings = 0
        
        for i, arg in enumerate(args):
            try:
                ty = idx[i]
            except KeyError:
                raise typy.TypeError("Invalid label: " + str(i), arg)
            elt_bindings = ctx.ana_pat(arg, ty)
            n_elt_bindings = len(elt_bindings)
            bindings.update(elt_bindings)
            n_bindings_new = len(bindings)
            if n_bindings_new != n_bindings + n_elt_bindings:
                raise typy.TypeError("Duplicate variable in pattern.", arg)
            n_bindings = n_bindings_new

        for keyword in keywords:
            label = keyword.arg
            try:
                ty = idx[label]
            except KeyError:
                raise typy.TypeError("Invalid label: " + label, keyword)
            value = keyword.value
            elt_bindings = ctx.ana_pat(value, ty)
            n_elt_bindings = len(elt_bindings)
            bindings.update(elt_bindings)
            n_bindings_new = len(bindings)
            if n_bindings_new != n_bindings + n_elt_bindings:
                raise typy.TypeError("Duplicate variable in pattern.", value)
            n_bindings = n_bindings_new

        return bindings

    def translate_pat_Call_constructor(self, ctx, pat, scrutinee_trans):
        scrutinee_trans_copy = astx.copy_node(scrutinee_trans)
        args, keywords = pat.args, pat.keywords
        idx = self.idx
        conditions = []
        binding_translations = _util.odict()
        for i, arg in enumerate(args):
            n = _util.odict_idx_of(idx, i)
            elt_scrutinee_trans = astx.make_Subscript_Num_Index(
                scrutinee_trans_copy,
                n)
            elt_condition, elt_binding_translations = ctx.translate_pat(
                arg, elt_scrutinee_trans)
            conditions.append(elt_condition)
            binding_translations.update(elt_binding_translations)
        
        for keyword in keywords:
            n = _util.odict_idx_of(idx, keyword.arg)
            elt_scrutinee_trans = astx.make_Subscript_Num_Index(
                scrutinee_trans_copy,
                n)
            elt_condition, elt_binding_translations = ctx.translate_pat(
                keyword.value, elt_scrutinee_trans)
            conditions.append(elt_condition)
            binding_translations.update(elt_binding_translations)

        condition = ast.BoolOp(
            op=ast.And(),
            values=conditions)

        return (condition, binding_translations)

    def syn_Attribute(self, ctx, e):
        idx = self.idx
        attr = e.attr
        try:
            ty = idx[attr]
        except KeyError:
            raise typy.TypeError("Cannot project component labeled " + attr, e)
        return ty 

    def translate_Attribute(self, ctx, e):
        n = _util.odict_idx_of(self.idx, e.attr)
        return ast.copy_location(ast.Subscript(
            value=ctx.translate(e.value),
            slice=ast.Num(n=n),
            ctx=ast.Load()
        ), e)

    def syn_Subscript(self, ctx, e):
        slice_ = e.slice
        if not isinstance(slice_, ast.Index):
            raise typy.TypeError("Must provide a single label.", slice_)
        value = slice_.value
        label = _read_label(value)
        try:
            ty = self.idx[label]
        except KeyError:
            raise typy.TypeError("Cannot project component labeled " + str(label), e)
        value.label = label
        return ty

    def translate_Subscript(self, ctx, e):
        value = e.value 
        label = e.slice.value.label
        n = _util.odict_idx_of(self.idx, label)
        return ast.copy_location(ast.Subscript(
            value=ctx.translate(value),
            slice=ast.Num(n=n),
            ctx=ast.Load()
        ), e)

    def syn_Compare(self, ctx, e):
        left, ops, comparators = e.left, e.ops, e.comparators
        for op in ops:
            if isinstance(op, (ast.Eq, ast.NotEq)):
                if not len(self.idx) == 0:
                    raise typy.TypeError("Can only compare unit values for equality.", e)
            elif not isinstance(op, (ast.Is, ast.IsNot)):
                raise typy.TypeError("Invalid comparison operator.", op)

        for e_ in _util.tpl_cons(left, comparators):
            if hasattr(e_, "match"): 
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

    # TODO: x + y
    # TODO: x - "label"
    # TODO: x - ("l1", "l2", "l3")
    # TODO: x % "label"
    # TODO: x % ("l1", "l2", "l3")
    # TODO: multi-projection, e.g. x['l1', 'l2', 'l3']

def _normalize_tuple_idx(idx):
    if not isinstance(idx, tuple):
        idx = (idx,)
    used_labels = set()
    for i, component in enumerate(idx):
        if isinstance(component, typy.TyExpr): # TODO KIND
            if i in used_labels:
                raise typy.TypeFormationError(
                    "Duplicate label: " + str(i))
            used_labels.add(i)
            yield (i, component)
            continue
        elif isinstance(component, slice):
            label = component.start
            ty = component.stop
            if component.step is not None:
                raise typy.TypeFormationError(
                    "Invalid tuple component: " + str(label))
        elif isinstance(component, tuple):
            if len(component) != 2:
                raise typy.TypeFormationError(
                    "Tuple component must have two components.")
            label = component[0]
            ty = component[1]
        else:
            raise typy.TypeFormationError(
                "Invalid component definition: " + str(component))

        if isinstance(label, six.string_types):
            if len(label) == 0:
                raise typy.TypeFormationError(
                    "String label must be non-empty.")
        elif isinstance(label, (int, long)):
            if label < 0:
                raise typy.TypeFormationError(
                    "Integer label must be non-negative.")
        else:
            raise typy.TypeFormationError(
                "Label must be a string or integer.")
        if label in used_labels:
            raise typy.TypeFormationError(
                "Duplicate label: " + str(i))
        used_labels.add(label)

        if not isinstance(ty, typy.Type):
            raise typy.TypeFormationError(
                "Component labeled " + label + " has invalid type specification.")

        yield (label, ty)

def _syn_idx_Tuple(cls, ctx, elts):
    for i, elt in enumerate(elts):
        if typy._is_intro_form(elt):
            ty = ctx.ana_intro_inc(elt, cls[...])
        else:
            ty = ctx.syn(elt)
        yield (i, ty)

def _read_label(key):
    if isinstance(key, ast.Name):
        return key.id
    elif isinstance(key, ast.Num):
        n = key.n
        if isinstance(n, (int, long)) and n >= 0:
            return n
        else:
            raise typy.TypeError("Invalid numeric label.", key)
    elif isinstance(key, ast.Str):
        s = key.s
        if s != "":
            return s
        else:
            raise typy.TypeError("Invalid string label.", key)
    else:
        raise typy.TypeError("Invalid label", key)

def _syn_idx_Dict(cls, ctx, keys, values):
    used_labels = set()
    for key, value in zip(keys, values):
        label = _read_label(key)
        if label in used_labels:
            raise typy.TypeError(
                "Duplicate label: " + str(label), key)
        used_labels.add(label)
        if typy._is_intro_form(value):
            ty = ctx.ana_intro_inc(value, tpl[...])
        else:
            ty = ctx.syn(value)
        key.label = label
        yield (label, ty)

def _syn_idx_Call_constructor(ctx, e):
    id = e.func.id
    if id != 'X':
        raise typy.TypeError("tpl only supports the X constructor", e.func)
    if e.starargs is not None:
        raise typy.TypeError("No support for starargs", e)
    if e.kwargs is not None:
        raise typy.TypeError("No support for kwargs", e)

    args = e.args
    keywords = e.keywords

    # process non-keywords
    for i, arg in enumerate(args):
        yield ctx.syn(arg)

    # process keywords
    for keyword in keywords:
        label = keyword.arg
        ty = ctx.syn(keyword.value)
        yield (label, ty)

def _labeled_translation(idx_mapping, arg_translation):
    lambda_translation = ast.Lambda(
        args=ast.arguments(
            args=[ast.Name(id='x', ctx=ast.Param())],
            vararg=None,
            kwarg=None,
            defaults=[]),
        body=ast.Tuple(
            elts=list(
                ast.Subscript(
                    value=ast.Name(
                        id='x',
                        ctx=ast.Load()),
                    slice=ast.Index(
                        value=ast.Num(n=n)),
                    ctx=ast.Load())
                for n in idx_mapping
            ),
            ctx=ast.Load()
        )
    )
    return ast.Call(
        func=lambda_translation,
        args=[arg_translation],
        keywords=[],
        starargs=[],
        kwargs=None
    )

unit = tpl[()]
