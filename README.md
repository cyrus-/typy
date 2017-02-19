NOTE: Tydy is still under development and not intended for public consumption in any way. Most of what's written below is still aspirational. See this paper for more details on what I'm working on: https://github.com/cyrus-/papers/blob/master/typy-2016/typy-2016.pdf.

tydy (pronounced "tidy") 
========================
tydy is a statically typed functional programming language (in the ML tradition) embedded into Python as a library.

```python 
import tydy

@tydy.component
def Hello():
	def greet(x : str): 
	    "Hello, " + x
	
	print(greet(x))
```

Definitions decorated with `@tydy.component` are parsed by Python, but given static and dynamic meaning by tydy.

Notice that the function `greet` does not use the `return` keyword. Like other functional programming languages, everything is an expression.

tydy also notably features:
* local type inference
* tuples and labeled tuples
* labeled sum types (variants)
* pattern matching
* parametric polymorphism
* clean interoperability with Python (you can even pattern match on Python values!)

If you're intrigued, check out the documentation for more details. If you need convincing, you might be interested in why you should tydy up.

I need *your* contributions and support:
* star, follow, join, share
* contribute to my patreon campaign
* convince your employer to sponsor tydy
* hire me to give a training seminar, provide support or consult on a tydy project
* write a library for tydy
* join the tydy team, there are lots of really interesting projects for anyone interested in programming language design and implementation.

Contributors
============

@cyrus-

License
=======
typy is released under the permissive MIT License, requiring only attribution in derivative works. See LICENSE for full terms.

