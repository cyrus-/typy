NOTE: Tydy is still under development and this repository is not yet intended for public consumption in any way. Most of what's written below is still aspirational. See this paper for more details on what I'm working on: https://github.com/cyrus-/papers/blob/master/typy-2016/typy-2016.pdf.

`tydy` (pronounced "tidy") 
==========================
Typed functional programming languages, like OCaml and Haskell, are semantically elegant, but real concerns about library availability and familiarity have limited their adoption. Consider these very real quotes:

> "You'll never get me to give up my obscure Python statistics packages!"

> "Mathematical elegance is great and all, but my 3D-printed toaster has Python bindings."

To address these all-too-real concerns, I'm building `tydy`: a typed functional programming language embedded into Python as a library!

Hello, World!
-------------
Here is the heart of a tydy'd up functional "Hello, World!":
```python
def greet(x : string): 
    "Hello, " + x + "!"
print(greet("World"))
```
Notice that the function `greet` does not need to explicitly `return`. Like other functional languages, `tydy` is *expression-oriented*. The return type is inferred.

The `tydy` code above lives inside a `tydy` component -- a Python definition decorated with `@tydy.component`. The full "Hello, World!" example therefore looks like this:
```python 
import tydy

@tydy.component
def Hello():
    def greet(x : string): 
        "Hello, " + x + "!"
    print(greet("World"))
```
The component body is parsed by Python, then typechecked and compiled (to Python, currently) by `tydy`. 

Installation
------------
To install `tydy`, you can just `pip install tydy`. Then, paste or type the code above into a file `hello.py` and run `python hello.py`. Currently, `tydy` requires Python 3.5+ (but the plan is to support Python 2.7+ in the future.)

Language Features
-----------------
Simple functions like `greet` are, of course, just the beginning. `tydy` has all the typed functional essentials... 
* algebraic datatypes (tuples, labeled tuples and labeled sums)
* pattern matching
* parametric polymorphism
* local type inference

...plus, fast and clean two-way interoperability with Python. The manual gives the full details. If you're already familiar with a typed functional language, you might be interested in a side-by-side comparison with Standard ML and OCaml.

Benefits
--------
Perhaps you aren't convinced. Allow me to elaborate.

### Functional Programming
The mathematical method has a proven track record across problem domains (to say the least!) Functional programming is merely the mathematical method applied to programming. Functional languages build immediately upon the basic mathematical concepts taught in high-school algebra and introductory logic, e.g.

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

