NOTE: Tidy is still under development and this repository is not yet ready for public consumption. Most development is going on in the underlying typy repository for now. 

---

Tidy
----
Typed functional programming is on the rise, but for many Python programmers it just isn't practical to switch outright to a typed functional language like OCaml or Haskell. Consider the following totally-not-made-up quotes:

   > "I'm not about to spend months rewriting all of these great Python statistics routines!"
      
   > "The rest of my research group uses Python, and we need to be able to interface with each other's code cleanly."

Tidy aims to address these concerns by embedding a typed functional programming language cleanly into Python, as a library. You can install Tidy by running `pip install tidy` today.

Hello, World!
-------------
Here is the heart of a tidy functional "Hello, World!":
```python
def hello(x : string): 
    "Hello, " + x + "!"
print(hello("World"))
```
Notice that the function `hello` does not need to explicitly `return` -- like other functional languages, Tidy is *expression-oriented*. The return type, `string`, is inferred. Tidy allows side effects, like `print`ing, anywhere (i.e. it can be considered an impure functional language in the ML tradition.)

Tidy code must appear inside a Tidy module:
```python 
import tidy

@tidy.module
def Hello():
    def hello(x : string): 
        "Hello, " + x + "!"
    print(hello("World"))
```
The module body is parsed by Python, then typechecked and translated to Python by `tidy` before it is evaluated. This needs to happen only once, even if `hello` is called many times.

Language Features
-----------------
Simple functions like `hello` are, of course, just the beginning. Tidy features all the typed functional essentials... 
* algebraic datatypes (tuples, labeled tuples and labeled sums)
* pattern matching
* parametric polymorphism
* local type inference

...plus, fast and clean two-way interoperability with Python. 

If you're already familiar with a typed functional language, you might be interested in a side-by-side comparison with  OCaml (TODO). The manual (TODO) gives the full details. If you're not familiar with a typed functional language, start with "what is typed functional programming, and why should I care?" (TODO)

License
-------
`tidy` is released under the permissive MIT License, requiring only attribution in derivative works.

