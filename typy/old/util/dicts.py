"""Dictionaries"""

# 
# DictStack
# 

class DictStack(object):
    def __init__(self, stack=None):
        if stack is None:
            stack = []
        self.stack = stack 

    def push(self, d):
        self.stack.append(d)
        return self

    def pop(self):
        return self.stack.pop()

    def peek(self):
        return self.stack[-1]

    def __getitem__(self, key):
        for d in reversed(self.stack):
            try:
                return d[key]
            except KeyError:
                pass
        raise KeyError(key)

    def __setitem__(self, key, value):
        self.peek()[key] = value

    def __contains__(self, key):
        for d in reversed(self.stack):
            if key in d: 
                return True
        return False 

# 
# odict
# 

def odict_idx_of(od, key):
    for idx, k in enumerate(od.iterkeys()):
        if k == key:
            return idx
    raise KeyError(key)

def odict_lookup_with_idx(od, key):
    for idx, (k, v) in enumerate(od.iteritems()):
        if k == key:
            return (idx, v)
    raise KeyError(key)

# OrderedDict implementation below is based on the 
# ordereddict module on pypi. Copyright notice reproduced below.

# Copyright (c) 2009 Raymond Hettinger
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
#     The above copyright notice and this permission notice shall be
#     included in all copies or substantial portions of the Software.
#
#     THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#     EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#     OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#     NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#     HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#     WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#     FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#     OTHER DEALINGS IN THE SOFTWARE.

from UserDict import DictMixin

class OrderedDict(dict, DictMixin):
    def __init__(self, *args, **kwds):
        if len(args) > 1:
            raise TypeError('expected at most 1 arguments, got %d' % len(args))
        self.clear()
        self.update(*args, **kwds)

    def clear(self):
        self.__end = end = []
        end += [None, end, end]         # sentinel node for doubly linked list
        self.__map = {}                 # key --> [key, prev, next]
        dict.clear(self)

    def __setitem__(self, key, value):
        if key not in self:
            end = self.__end
            curr = end[1]
            curr[2] = end[1] = self.__map[key] = [key, curr, end]
        dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        key, prev, next = self.__map.pop(key)
        prev[2] = next
        next[1] = prev

    def __iter__(self):
        end = self.__end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]

    def __reversed__(self):
        end = self.__end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]

    def popitem(self, last=True):
        if not self:
            raise KeyError('dictionary is empty')
        if last:
            key = reversed(self).next()
        else:
            key = iter(self).next()
        value = self.pop(key)
        return key, value

    def __reduce__(self):
        items = [[k, self[k]] for k in self]
        tmp = self.__map, self.__end
        del self.__map, self.__end
        inst_dict = vars(self).copy()
        self.__map, self.__end = tmp
        if inst_dict:
            return (self.__class__, (items,), inst_dict)
        return self.__class__, (items,)

    def keys(self):
        return list(self)

    setdefault = DictMixin.setdefault
    update = DictMixin.update
    pop = DictMixin.pop
    values = DictMixin.values
    items = DictMixin.items
    iterkeys = DictMixin.iterkeys
    itervalues = DictMixin.itervalues
    iteritems = DictMixin.iteritems

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, self.items())

    def copy(self):
        return self.__class__(self)

    @classmethod
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value
        return d

    def __eq__(self, other):
        if self is other: return True
        elif isinstance(other, OrderedDict):
            items = self.items()
            other_items = other.items()
            if len(items) != len(other_items):
                return False
            for p, q in zip(items, other_items):
                if p != q:
                    return False
            return True
        else: return dict.__eq__(self, other)

    def __ne__(self, other):
        return not self == other

odict = OrderedDict

class ImmutableException(Exception): pass

class ImmOrderedDict(OrderedDict):
    """An ordered dict with the mutation methods disabled."""
    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError("Expected at most 1 arguments, got %d" % len(args))
        OrderedDict.clear(self)
        OrderedDict.update(self, *args, **kwargs)
        self._init_done = True

    _init_done = False
    def clear(*a, **k): raise ImmutableException()
    def copy(*a, **k): raise ImmutableException()
    def pop(*a, **k): raise ImmutableException()
    def popitem(*a, **k): raise ImmutableException()
    def setdefault(*a, **k): raise ImmutableException()
    def update(*a, **k): raise ImmutableException()
    def __setitem__(self, *a, **k): 
        if self._init_done: raise ImmutableException()
        else: return OrderedDict.__setitem__(self, *a, **k)
    def __delitem__(*a, **k): raise ImmutableException()

    def __hash__(self):
        return hash(self.items())

class ImmDict(ImmOrderedDict):
    """An ImmOrderedDict where equality and hashing is unordered."""
    _set_of = None

    def _get_set_of(self):
        _set_of = self._set_of
        if _set_of is None:
            _set_of = self._set_of = set(self.items())
        return _set_of

    def __eq__(self, other):
        if self is other: return True
        elif isinstance(other, ImmDict):
            return self._get_set_of() == other._get_set_of()
        else:
            return OrderedDict.__eq__(self, other)

    def __hash__(self):
        return hash(self._get_set_of())

