NOTE: Tydy is still under development and this repository is not yet intended for public consumption in any way. Most of what's written below is still aspirational. See this paper for more details on what I'm working on: https://github.com/cyrus-/papers/blob/master/typy-2016/typy-2016.pdf.

`tydy` (pronounced "tidy") 
==========================
Typed functional programming languages, like OCaml and Haskell, are a joy to work with, but concerns about library availability and familiarity often discourage adoption. Enter `tydy`, a typed functional programming language embedded  into Python, as a library.

For example, consider the following variation on "Hello, World!":
```python
def greet(x : string): 
    "Hello, " + x + "!"
print(greet("World"))
```
Notice that the function `greet` does not need to use the `return` keyword. Like other functional languages, `tydy` is *expression-oriented*. (Later, you'll see that some semantic expressions span multiple syntactic statements.)

`tydy` code must be placed inside a `tydy` component, which is simply a Python definition decorated with `@tydy.component`. The body is parsed by Python, but given static and dynamic meaning by `tydy`. The full "Hello, World!" example therefore looks like this:
```python 
import tydy

@tydy.component
def Hello():
    def greet(x : string): 
        "Hello, " + x + "!"
    print(greet("World"))
```
To install `tydy`, you can just `pip install tydy`. Stick the code above into a file `hello.py` and run `python hello.py`. The whole thing is a library -- typechecking and compilation occurs "just-in-time" (once).

Language Features
-----------------
Strings and simple functions like `greet` are, of course, just the beginning. `tydy` features the essential typed functional goodies...
* algebraic datatypes (i.e. tuples, labeled tuples and labeled sums)
* pattern matching
* parametric polymorphism
* local type inference

...plus, **fast and clean two-way interoperability with Python**.

Benefits
--------
### Functional Programming
The mathematical method has a proven track record across problem domains, to say the least. Functional programming is merely the mathematical method applied to programming. In other words, functional languages build immediately upon the basic mathematical concepts taught in high-school algebra and introductory logic, e.g.

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

Join the Fun
------------
I think `tydy` could bring statically typed functional programming to a huge number of people. Help make it happen:
* star this repository, share, join our gitter
* write a tydy library (ideas and progress)
* contribute to the patreon campaign, individually or as an organizational sponsor
* hire me to give a training seminar, provide support or consult
* give a talk about tydy to your local Python users group, your academic department, or to a conference (example slides)
* join the tydy team -- there are lots of really interesting projects for anyone interested in designing and implementing programming languages and tools. 

License
-------
typy is released under the permissive MIT License, requiring only attribution in derivative works. See LICENSE for full terms.

