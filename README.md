Tydy 
====
Tydy (pronounced "tidy") is a statically typed, functional-first programming language in the ML tradition. ``tydy`` (pronounced "tie dye") is an implementation of Tydy as a Python library.

You can install ``tydy`` with ``pip install tydy``. Here is the obligatory "Hello, world!" program, which should be fairly self-explanatory:

```python
from tydy import module

@module
def Main():
    print("Hello, world!")
```

Put that into ``hello.py`` then run ``python hello.py`` at the shell to make sure everything installed correctly. This will print ``Hello, world!``.

Let's look at a more idiomatic Tydy program.

```python
from tydy import interface, module

@interface
def IGreeting():
    greeting [: string > string]
    """Produces a greeting."""

@module
def Hello():
	"""An implementation of IGreeting."""
    _ [: IGreeting]

    def greeting(name):
        "Hello, " + name + "!"

@module
def Main():
	print(Hello.greeting("tydy"))

    # Static type errors:
	# print(Hello.greetng("tydy"))
	# print(greeting("tydy")) 
    # print(Hello.greeting(42))
```

Here, we've defined:
  - a Tydy interface, ``IGreeting`` 
  - a Tydy module that implements that interface, ``Hello`` 
  - and another Tydy module, ``Main``, that we are only evaluating for its effect, namely to print the result of applying the function ``Hello.greeting`` to the string ``"tydy"``

Put this example into ``greet.py`` then run ``python greet.py`` at the shell to say hello.

Here's what's happening: the definition of ``IGreeting``, together with the interface ascription ``_ [: IGreeting]``, compels ``Hello`` to define a value labeled ``greeting`` of type ``string > string``. This type classifies functions that take a ``string`` as input, and produce a ``string`` as output. We use the ``def`` form to simultaneously define a value of this type and label it ``greeting``.

Notice that in the definition of ``Hello.greeting``, no type annotations were necessary -- the interface ascription is sufficient to determine what the type of ``name`` should be in the body of ``greeting``. Notice also that the body of ``greeting`` does not use the ``return`` keyword. The final term in the body of a function is the value that is returned. 

Uncomment the lines at the end of the example above to see what happens when you write ill-typed expressions. Notice in each case that, although the lines in question appear after the well-typed print expression just discussed, nothing is printed when there is a type error (other than the error message itself). The checks are truly at compile-time (which happens to coincide with the top-level Python script's run-time in this mode of use of ``tydy``).

#### More Features

The example above is but the tip of the iceberg, of course. Like other functional languages in the ML tradition, Tydy allows you to:

* Define **recursive datatypes**
* Deconstruct values by **pattern matching**
* Define **mutable reference cells**, **fields**, **arrays** and **stack assignables** for when you want to do some imperative programming
* Package both **types** and **values** into modules
  * Tydy interfaces behave like ML signatures, i.e. **interface checking is structural** (if a module statically quacks like an ``IDuck``, it is an ``IDuck``)
  * An interface can **selectively abstract away the identity of a type** defined in a module, which makes it possible to reason locally about internal invariants (see example below)
  * Unlike many other ML descendents, **modules are themselves values**

If you're not familiar with some of these ideas, don't worry, you're not alone. For reasons that have little to do with [their intrinsic value](http://queue.acm.org/detail.cfm?id=2038036), they have been slow to make their way into major programming languages. Tydy is an effort to change that, because:
 * Tydy adopts **Python's syntax** directly (although it creatively repurposes it at times, as you can see above!)
 * **Every Python value is also a Tydy value**, of a type called ``dy`` (pronounced "dee"). You can pattern match over values of this type, in addition to all the usual Python operations. This means that **all Python libraries** are available to you.
   * If you use ``tydy``, which is presently the only implementation of Tydy, then you can use any library that your Python run-time understands what to do with, including ones that use foreign functions (e.g. ``numpy`` etc.)
   * This introduces absolutely no run-time overhead -- nothing is "boxed" or otherwise intercepted. You're as close to the metal as something running inside a Python run-time can be.

Tydy diverges from other descendents of ML in how it approaches a few things as well. The most pervasive semantic difference is that it has an easy-to-understand _bidirectional type system_, in lieu of a Hindley-Milner-style type inference mechanism. We'll detail some of the powerful conveniences this enables later, but in short:
 * **Type annotations are rarely needed** (mostly only at interface boundaries, which is good because that doubles as documentation)
 * **Introductory forms** (e.g. string, number, list and set literals) **and elimination forms** (e.g. field projection) **are available at many types**. Indeed, this is a key part of why interfacing with Python libraries has little or no syntactic overhead. 
   * This **includes abstract types** -- in particular:
     * You can **access values that are known to be packaged alongside an abstract type using field projection syntax**. For example, ``n.succ.succ.to_num`` rather than ``AbsNat.to_num(AbsNat.succ(AbsNat.succ(n)))`` (see example below).
     * You can also **pattern match over values of abstract type**, if its interface defines a mapping onto a suitable recursive datatype (also described below).
 * ``tydy`` is able to report **clear, localized type errors** (no unification variables)

##### A who in the what now?
Tydy is still an emerging language, so for now, I'm going to assume that you're at least vaguely familiar with some of the things I just mentioned.

If you aren't, don't worry, I still like you and want you to like me. Hopefully, we'll be able to put together some truly introductory-level learning material using Tydy soon. But for now, I'll have to direct you to learning material on languages like Standard ML, OCaml, Scala or Haskell, in decreasing order of similarity to Tydy. Knowing at least one of these is a good idea in any case, even if you don't end up using Tydy, so it won't be for naught.


Trees
===============
Alright, let's show off some of the fun features.

```python
from tydy import module

@module
def Example():
    numtree == Empty | Node(numtree * numtree) | Leaf(num)
    """the type of binary trees with numbers at the leaves"""
    
    a_lil_tree [: numtree] = Node(Leaf(3), Node(Leaf(4), Leaf(5)))

    def sum_leaves(tree):
		"""sums up all the leaves of the tree"""
		sum_leaves [: numtree > num] 
		~[tree] # pattern match on tree
		with Empty: 0
        with Node(left, right):
            left_sum = sum_leaves(left)
            right_sum = sum_leaves(right)
            left_sum + right_sum
        with Leaf(n): n
```

(TODO: more descriptions)

Here is the same thing written in OCaml:
```ocaml
module Example = 
struct
    (* the type of binary trees with numbers at the leaves *)
    type numtree = Empty | Node of numtree * numtree | Leaf of int

    let a_lil_tree : numtree = Node(Leaf 3, Node(Leaf 4, Leaf 5))  

    (* sums up the leaves of the tree *)
    let rec sum_leaves(tree : numtree) = 
        match tree with 
        | Empty -> 0
        | Node(left, right) -> 
            let left_sum = sum_leaves left in 
            let right_sum = sum_leaves right in 
            left_sum + right_sum
        | Leaf(n) -> n
end
```

and in Standard ML:
```sml
structure Example =
struct
  datatype numtree = Empty | Node of numtree * numtree | Leaf of int

  val a_lil_tree : numtree = Node(Leaf 3, Node(Leaf 4, Leaf 5))

  fun sum_leaves(tree : numtree) = 
      case tree of 
	    Empty => 0
	  | Node(left, right) => 
	      let 
		    val left_sum = sum_leaves left
			val right_sum = sum_leaves right
		  in
		    left_sum + right_sum
		  end
	  | Leaf(n) => n
end
```

Interaction with Python
=======================
Not the best example:

```python
import sys
from typy.std import fn, dyn

@fn
def main(argv):
	{argv : dyn}
    match[argv]
	with [str(_), str(name)] or [str(_), str(_), str(name)]: 
		print("Hello, " + name + "!")
    with [_]:
		print("Hm, something went wrong.")

main(sys.argv)
```

Hypothetical error message once I get dyn AND pattern matching exhaustiveness checking together:

```
Exception: typy.TyErr
Lines 10-12.
typy.TyErr: Pattern matching non-exhaustive.
Here are some examples of patterns that are not matched:
  
    with None: _
    with True or False: _
    with 0 | 1 | 2 | int(_): _
    with "" | "abc" | str(_): _
    with () | (_,) | (_, _) | tuple(_): _
    with {} | {_: _} | {_: _, _: _} | dict(_): _
	with [] | [_] | list(_): _
    with ast.Func[_ | _.func is ast.Name[_ | _.id is id], 
                      match[_.args]]:
        with []: _
        with _: _

This list is not exhaustive.
```

```python
if isinstance(e, ast.Func) and isinstance(e.func, ast.Name):
    id = e.func.id
    if isinstance(e.func.args, []) and len(e.func.args) == 0:
        _
    else:
        _
```

Differences Between Ocaml and typy
==================================
    Summary of Syntactic Differences
    Equirecursive vs. Isorecursive Types
        type [list(+a)] = finsum[
            Nil,
            Cons: (+a, list(+a))
        ]
        type [t(+a)] = finsum[
            Nil,
            Cons: (+a, list(+a))
        ]
        # Isorecursive: list(+a) and t(+a) are different types.
        # Equirecursive: list(+a) and t(+a) are equal types.
        # Infinite regress is prevented by forcing all 
        # recursive type definitions to immediately apply a type
        # operator, so definitions like this are not allowed:
        type [list(+a)] = list(+a)

        # types like this can be defined
        type [t] = (num, t)

        # no self-reference via binding
        x [: t] = (0, x) # TyErr: x is unbound
        
        # you can do stuff like this, but you'll just get 
        # an infinite loop
        def f(x):
            {num} > t
            (x, f(x+1))
        f(0) # = (0, f(1)) = (0, (1, f(2)) = ...

        xrange [: coroutine[(num, num, num), num]]

    Bidirectional Typing vs. Local Type Inference
        Introductory Forms
    Currying and Named Arguments
    Components vs. Modules vs. Objects
        Generative component functions
        First-class modules (~ like 1ML)
        Operations on values of abstract type
        Subtyping

Implementation
==============

The ``@module`` function annotation is where the magic starts. It's not, like, real magic though -- ``typy.module`` just uses Python's standard ``inspect`` and ``ast`` modules to retrieve and parse the source of the Python function it decorates, then throws the function itself into the garbage. It's body will never be evaluated. (Play with ``ast.dump(ast.parse(inspect.getsource(f)))`` if you're curious about what the syntax trees look like!) 

Contributors
============

@cyrus-

License
=======
Copyright 2016 Cyrus Omar.

typy is released under the permissive MIT License, requiring only attribution in derivative works. See LICENSE for full terms.

