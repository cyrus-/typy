import tidy

# # # # LAYER PROBLEM # # # # 
"""Given a list of values, and a function that maps values to 
      Low | Med | High
produce a list where all the low values are at one end, the high
values at the other and the medium values in between."""

# Python version (semantically clean, full checks)
class Level(object): pass
class Low(Level): pass
class Med(Level): pass
class High(Level): pass

def layer_python(xs, f):
    if not iterable(xs): raise Exception("xs must be iterable")
    if not callable(f):  raise Exception("f must be callable")
    low, med, high = [], [], []
    for x in xs:
        fx = f(x)
        if isinstance(fx, Low): low.append(x)
        elif isinstance(fx, Med): med.append(x)
        elif isinstance(fx, High): high.append(x)
        else: raise Exception("f(x) was invalid: " + str(fx))
    low.extend(med)
    low.extend(high)
    return low

# Python version (semantically clean, assume good args)
class Level(object): pass
class Low(Level): pass
class Med(Level): pass
class High(Level): pass

def layer_python(xs, f):
    low, med, high = [], [], []
    for x in xs:
        fx = f(x)
        if isinstance(fx, Low): low.append(x)
        elif isinstance(fx, Med): med.append(x)
        elif isinstance(fx, High): high.append(x)
    low.extend(med)
    low.extend(high)
    return low

# Python version (sloppy)
def layer_python2(xs, f):
    low, med, high = [], [], []
    for x in xs:
        fx = f(x)
        if fx == "Low": low.append(x)
        elif fx == "Med": med.append(x)
        elif fx == "High": high.append(x)
    low.extend(med)
    low.extend(high)
    return low

@tidy.module
def Layer():
    # Tidy version (imperative)
    def layer_imperative(xs : List(+A), f : +A > (Low | Med | High)):
        low, med, high : MList(+A) = [], [], []
        for x in xs:
            match: f(x)
            with Low: low.append(x)
            with Med: med.append(x)
            with High: high.append(x)
        low.extend(med)
        low.extend(high)
        low.frozen()

    # Tidy version (functional)
    def layer_functional1(xs : List(+A), f : +A > (Low | Med | High)):
        low, med, high : List(+A) = xs.fold(base, rec)
        with base, rec in above as follows:
            base = [], [], []
            def rec(x, out):
                low, med, high = out
                match: f(x)
                with Low: low.appended(x), med, high
                with Med: low, med.appended(x), high
                with High: low, med, high.appended(x)
        low.extended(med).extended(high)

    # Tidy version (functional, no where)
    def layer_functional2(xs : List(+A), f : +A > (Low | Med | High)):
        t [type] = List(+A) * List(+A) * List(+A)
        base : t = [], [], []
        def rec(x : +A, out : t):
            low, med, high = out
            match: f(x)
            with Low: low.appended(x), med, high
            with Med: low, med.appended(x), high
            with High: low, med, high.appended(x)
        low, med, high = xs.fold(base, rec)
        low.extended(med).extended(high)


