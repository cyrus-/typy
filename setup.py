from distutils.core import setup

setup(
	name='typy',
	version='0.2.0',
	author='Cyrus Omar',
	author_email='comar@cs.cmu.edu',
	packages=('typy',),
	py_modules=('typy',),
	url='http://www.github.com/cyrus-/typy',
	license='MIT',
	description='A programmable static type system, embedded into Python.',
	long_description='',
	install_requires=('astunparse','six','ordereddict')
)
