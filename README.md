NOTE: tydy is still under development and this repository is not yet intended for public consumption in any way.

---

![tydy: simply typed functional programming inside Python](https://github.com/cyrus-/tydy/raw/master/tydy-logo-goudy.png)

  
---
Simply typed functional programming is the practice of building programs up from simple mathematical primitives like tuples, finite variants and functions (rather than fundamentally _ad hoc_, machine-oriented primitives like mutable objects and nullable references.) The promised benefits are substantial.

Unfortunately, popular programming languages like Python don't yet have great support for typed functional programming. Conversely, typed functional programming languages like OCaml and Haskell don't yet have nearly as much library support or social inertia. Consider these totally-not-made-up quotes:

   > "You'll never get me to give up my obscure Python statistics packages!"

   > "Mathematical elegance is nice and all, but my 3D-printed toaster has Python bindings."

`tydy` aims to address this problem by embedding a typed functional programming language cleanly into Python, as a library. Install `tydy` by running `pip install tydy`.

Hello, World!
-------------
Here is the heart of a `tydy`'d up functional "Hello, World!":
```python
def hello(x : string): 
    "Hello, " + x + "!"
print(hello("World"))
```
Notice that the function `hello` does not need to explicitly `return` -- like other functional languages, `tydy` is *expression-oriented*. The return type, `string`, is inferred. `tydy` allows side effects, like `print`ing, anywhere (i.e. it can be considered an impure functional language in the ML tradition.)

`tydy` code lives inside `tydy` components:
```python 
import tydy

@tydy.component
def Hello():
    def hello(x : string): 
        "Hello, " + x + "!"
    print(hello("World"))
```
The component body is parsed by Python, then typechecked and compiled (to Python) by `tydy`. This needs to happen only once, even if some other component calls `hello` many times.

Installation
------------
To install `tydy`, you can just `pip install tydy`. Then, paste the code above into a file `hello.py` and run `python hello.py`. Currently, `tydy` requires Python 3.5+ (but the plan is to support Python 2.7+ in the near future.)

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
I think `tydy` could bring statically typed functional programming to the masses. Help make it happen:
* star this repository, share, join our gitter
* write a tydy library (ideas and progress)
* contribute to the patreon campaign, individually or as an organizational sponsor
* hire me to give a training seminar, provide support or consult
* give a talk about tydy to your local Python users group, your academic department, or to a conference (example slides)
* join the tydy team -- there are lots of really interesting projects for anyone interested in designing and implementing programming languages and tools. 

License
-------
`tydy` is released under the permissive MIT License, requiring only attribution in derivative works. See LICENSE for full terms.

