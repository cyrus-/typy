NOTE: tydy is still under development and this repository is not yet intended for public consumption in any way.

---
Typed functional programming is a programming paradigm rooted in the mathematical tradition. The primitive data structures are simple and immutable -- tuples, finite variants and functions, primarily -- and types statically mediate abstraction.

Many of us in the language design community are convinced that typed FP is, in principle, ready for mainstream adoption. Unfortunately, mainstream programming languages like Python have been slow to support the paradigm. Languages like OCaml and Haskell do support typed FP quite well, but they remain far behind in terms of library support and social inertia. These things turn out to be pretty important in practice. Consider the following totally-not-made-up quotes:

   > "You'll never get me to give up or rewrite my obscure Python statistics packages!"
   
   > "Mathematical elegance is nice and all, but my 3D-printed toaster only has Python bindings."
   
   > "The rest of my research group uses Python, and we need to be able to call into each other's code!"

Tidy aims to address these sorts of concerns head-on by embedding a typed functional programming language cleanly into Python, as a library. You can install `tidy` by running `pip install tidy` today.

Hello, World!
-------------
Here is the heart of a `tydy`'d up functional "Hello, World!":
```python
def hello(x : string): 
    "Hello, " + x + "!"
print(hello("World"))
```
Notice that the function `hello` does not need to explicitly `return` -- like other functional languages, `tydy` is *expression-oriented*. The return type, `string`, is inferred. `tydy` allows side effects, like `print`ing, anywhere (i.e. it can be considered an impure functional language in the ML tradition.)

`tydy` code must appear inside a `tydy` component:
```python 
import tydy

@tydy.component
def Hello():
    def hello(x : string): 
        "Hello, " + x + "!"
    print(hello("World"))
```
The component body is parsed by Python, then typechecked and translated to Python by `tydy` before it is evaluated. This needs to happen only once, even if some other component calls `hello` many times.

Language Features
-----------------
Simple functions like `hello` are, of course, just the beginning. `tydy` has all the typed functional essentials... 
* algebraic datatypes (tuples, labeled tuples and labeled sums)
* pattern matching
* parametric polymorphism
* local type inference

...plus, fast and clean two-way interoperability with Python. 

The manual gives the full details. If you're already familiar with a typed functional language, you might be interested in a side-by-side comparison with Standard ML and OCaml.

Let's make this happen.
-----------------------
I think `tydy` could bring typed functional programming to a massive new audience. Here's how you can help make it happen:
* star this repository, share, join our gitter
* write a tydy library (ideas and progress)
* give a talk about tydy to your local Python users group, your academic department, or to a conference (example slides)
* join the tydy team -- there are lots of really interesting projects for anyone interested in designing and implementing programming languages and tools. 

It would really help if there was money flowing into the project as well. Here are some ways you can help:
* contribute individually to the patreon campaign 
* become an organizational sponsor of tydy, and enjoy prominent placement on the website and README
* hire me to give a training seminar, provide support or consult

License
-------
`tydy` is released under the permissive MIT License, requiring only attribution in derivative works. See LICENSE for full terms.

