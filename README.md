NOTE: Tydy is still under development and this repository is not yet intended for public consumption in any way. Most of what's written below is still aspirational. See this paper for more details on what I'm working on: https://github.com/cyrus-/papers/blob/master/typy-2016/typy-2016.pdf.

`tydy` (pronounced "tidy") 
==========================
Typed functional programming languages encourage you to structure your programs mathematically, using simple primitives like tuples, finite variants and functions, rather than fundamentally complicated things like mutable objects, possibly-null references and multiple inheritance. The benefits are substantial: fewer errors, clearer code and peace of mind.

Unfortunately, popular programming languages like Python don't yet have great support for typed functional programming and  typed functional programming languages like OCaml and Haskell don't have nearly as much library support and social inertia. Consider these totally-not-made-up quotes:

> "You'll never get me to give up my obscure Python statistics packages!"

> "Mathematical elegance is nice and all, but check this out, my 3D-printed toaster has Python bindings."

> "What's an OCaml?"

`tydy` aims to accelerate the adoption of typed functional programming by embedding a typed functional programming language cleanly into Python, as a library.

Hello, World!
-------------
Here is the heart of a tydy'd up functional "Hello, World!":
```python
def hello(x : string): 
    "Hello, " + x + "!"
print(hello("World"))
```
Notice that the function `hello` does not need to explicitly `return`. Like other functional languages, `tydy` is *expression-oriented*. The return type, `string`, is inferred. Following the approach of impure functional languages in the ML tradition, we allow side effects, like `print`ing, anywhere.

The `tydy` code above lives inside a `tydy` component -- a Python definition decorated with `@tydy.component`. The full "Hello, World!" example therefore looks like this:
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

Benefits
--------
Perhaps you aren't convinced. Allow me to elaborate.

### Functional Programming
The mathematical method has been the engine of technological innovation for centuries. Functional programming is the mathematical method applied to programming. In particular, functional languages build immediately upon basic mathematical concepts taught in high-school algebra and introductory logic:

* variables are placeholders given meaning by substitution
* functions map from input of some type to output of some possibly different type
* tuples allow you to group together multiple values, corresponding to the elementary logical concept of *conjunction*
* sums capture the elementary logical concept of *disjunction*, e.g. a natural number can be either zero or the successor of another natural number.

### Static Typing
The usual arguments apply:
* You'll discover errors sooner.
* You won't have to deal with `None` creeping up where it shouldn't.
* Your code will run slightly faster (it's still running under Python, but the `tydy` compiler can choose fast data representations underneath.)
* You will have to write fewer tests.
* You will be less worried about test coverage.

### Python Interoperability
Because `tydy` is defined by translation to Python and understands Python values, interfacing with Python code is easy and doesn't cost anything. There is a lot of Python code out there, especially in areas like scientific computing, so this is a huge practical win.

Furthermore, you can embed `tydy` code anywhere within a Python program, not just at the top level of a Python file. That means that you can integrate `tydy` into a codebase incrementally. (This is where languages like Scala and F# fall short -- portions of a codebase written in Java/C# cannot always interface naturally with portions written in Scala/F#.)

Let's make this happen.
-----------------------
I think `tydy` could bring statically typed functional programming out of the shadows. Help make it happen:
* star this repository, share, join our gitter
* write a tydy library (ideas and progress)
* contribute to the patreon campaign, individually or as an organizational sponsor
* hire me to give a training seminar, provide support or consult
* give a talk about tydy to your local Python users group, your academic department, or to a conference (example slides)
* join the tydy team -- there are lots of really interesting projects for anyone interested in designing and implementing programming languages and tools. 

License
-------
`tydy` is released under the permissive MIT License, requiring only attribution in derivative works. See LICENSE for full terms.

