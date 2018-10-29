"""Useful utilities used internally or useful to extensions."""

def tpl_cons(hd, tl):
    yield hd
    for x in tl:
        yield x 

def contains_ellipsis(idx):
    if idx is Ellipsis: 
        return True
    elif isinstance(idx, tuple):
        for item in idx:
            if item is Ellipsis: 
                return True
    return False 

_py_fn_type = type(lambda x: x) # can use any function
def is_py_fn(obj):
    return isinstance(obj, _py_fn_type)

def fn_argcount(obj):
    return obj.func_code.co_argcount

