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

def _dict_pos_of(key, d):
    for i, k in enumerate(d.keys()):
        if key == k: return i

def _seq_pos_of(key, seq):
    for i, k in enumerate(seq):
        if key == k: return i

def seq_cons(hd, tl):
    yield hd
    for x in tl:
        yield x 

