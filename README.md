NOTE: Tydy is still under development and this repository is not yet intended for public consumption in any way. Most of what's written below is still aspirational. See this paper for more details on what I'm working on: https://github.com/cyrus-/papers/blob/master/typy-2016/typy-2016.pdf.

`tydy` (pronounced like "tidy") 
===================================================
`tydy` is a statically typed functional programming language embedded dynamically into Python.

```python 
import tydy

@tydy.component
def Hello():
	def greet(x : str): 
	    "Hello, " + x
	
	print(greet(x))
```

Definitions decorated with `@tydy.component` are parsed by Python, but given static and dynamic meaning by `tydy`. For example, notice that the function `greet` does not use the `return` keyword -- like other functional programming languages, everything is an expression.

Features
--------
* local type inference
* tuples and labeled tuples
* labeled sum types (variants)
* pattern matching
* parametric polymorphism
* clean interoperability with Python (you can even pattern match on Python values!)

If you're intrigued, check out the documentation for more details. If you need convincing, you might be interested in why you should tydy up.

Contribute!
-----------
I think `tydy` could bring statically typed functional programming to the masses, but for that to happen, I need you to help:
* star this repository, share, join our gitter
* write a tydy library (ideas and progress)
* contribute to my patreon campaign, individually or as an organizational sponsor
* hire me to give a training seminar, provide support or consult
* give a talk about tydy to your local Python users group, your academic department, or to a conference (example slides)
* join the tydy team -- there are lots of really interesting projects for anyone interested in designing and implementing programming languages and tools. 

License
-------
typy is released under the permissive MIT License, requiring only attribution in derivative works. See LICENSE for full terms.

