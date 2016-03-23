from typy import component

component Tree:
    component Internal:
        type tree(+a) = ...
        def map:
            tree [: tree(+a)]
            f    [: +a -> +b]

             % """def"""
             - _
            """ABC"""
            f    [: +a > +b]
            yield tree(+b)
            
            map : {tree(+a), +a -> +b} -> tree(+b)
            match tree
            | Empty -> tree
            | Node(v, children) -> 

@interface
def IInternalTree():
    with map:
        tree [: tree(+a)]
        f    [: +a > +b]
        _    >> tree(+b)

@component
def Tree():
    @component
    def Internal():
        """Trees with values at internal nodes."""
        tree(+a) [type] = [
            + Empty
            + Node(+a, vec[tree(+a)])
        ]

        def Leaf_(x):
            x      [: +a]
            _      > tree(+a)
            Node(+a, [])

        def map(tree, f):
            (hd, tl)  [: tree(+a)] 
            f         [: +a > +b] 
            _         > tree(+b)
            match[tree]
            with Empty: tree
            with Node(v, children):
                Node(f(v), children.map(map(_, f)))
            with Leaf(v):
                Leaf(f(v))

        folder(+a, +b) [type] = {
            empty : +b,
            node : (+a, vec[+b]) > +b,
            leaf : +a > +b
        }
        def fold(tree, folder):
            tree   [: tree(+a)]
            f      [: folder(+a, +b)]
            fold > [: +b]
            match[tree]
            with Empty:
                folder.empty
            with Node(v, children):
                children_v = children.fold(fold(_, folder))
                folder.node(v, children_v)
            with Leaf(v):
                folder.leaf(v)

    @component
    def InternalExamples():
        inumtree [type] = Internal.tree(num)
        Leaf_ = Internal.Leaf_

        empty [: inumtree] = Empty
        one_leaf [: inumtree] = Leaf_(1)
        three_ones [: inumtree] = Node(3, 
            [Leaf_(1), Leaf_(1), Leaf(1)])

    @component
    def External():
        """Trees with values only at leaves."""
        tree(+a) [type] = [
            + Empty
            + Node(vec[tree(+a)])
            + Leaf(+a)
        ]

        def map(tree, f):
            {tree(+a), +a > +b} > tree(+b)
            match[tree]
            with Empty: tree
            with Node(children): Node(children.map(map(_, f)))
            with Leaf(v): Leaf(f(v))

        folder(+a, +b) [type] = {
            empty : +b,
            node : vec[+b] > +b,
            leaf : +a > +b
        }
        def fold(tree, folder):
            {tree(+a), folder(+a, +b)} > +b
            match[tree]
            with Empty:
                folder.empty
            with Node(children):
                folder.node(children.fold(fold(_, folder)))
            with Leaf(v):
                folder.leaf(a)

