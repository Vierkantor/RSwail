.. _swail-reference:

Language Reference
******************

Declarations
============

To start this somewhat circular explanation, a declaration is an operation
which creates a value (constructing) and gives a name to that value (defining).
Each declaration happens in some scope, and using the name in the same scope,
refers to that value.

Data structures
---------------

Data structures, or structs, are similar to the algebraic data types of
Haskell, as they represent a sum of products. Most language features are
defined in terms of these structs. A simple example of a data structure is::

	struct maybe():
		nothing()
		just(value)

Any instance of the ``maybe`` struct is a ``nothing``, or a ``just``, together
with a single value. The members of this struct, i.e. ``nothing`` and ``just``,
work like functions that make instances.

Functions
---------

Functions are the other major component of the most basic programs. They are
more similar to the imperative functions of Python than the pure functions of
Haskell, as they can do multiple sequential calculations and affect state
outside the function scope. To be more precise, a function consists of a header
and a body.  The header is a description of the function, defining which
parameters it has.  When executing a function, a scope is created based on the
scope the function was declared, parameters are defined by the arguments, and
the body is executed in the scope.

Here are two functions that operate on a ``cons-list`` structure::

	def append(first_items, final_item):
		match first_items
		case cons-list.empty():
			cons-list.cons(final_item, list.empty())
		case cons-list.cons(`head, `tail):
			cons-list.cons(head, append(tail, final_item))
	
	def reverse(to_reverse):
		match to_reverse
		case cons-list.empty():
			cons-list.empty()
		case cons-list.cons(`head, `tail):
			append(reverse(tail), head)

The result of a function is the result of the last statement executed in the
body.

Custom declarations
-------------------

In fact, a declaration isn't fundamentally different from a function call. In
the case of a declaration, the arguments to the call are the name to be defined
and the syntax tree for all arguments (including the block). If you somehow
urgently needed to make a declaration that works like assignments (except for
all the sugar implemented in Swail), you can write::

	def let(name, values, _):
		values[0]
	
	# an example assignment
	let answer(42)

Expressions
===========

A statement is a piece of code that can be executed on its own. Apart from
declarations, the other type of statements are expressions. Expressions come in
three flavors: values, names, calling and matching.

Values
------

A value is simply an instance of some data structure defined before. For
example::

	integer = 37
	string = "Hello, World"
	complicated-value = [("a", "tuple"), {"a dict": 42}]

Names
-----

Names allow you to look up a value that you've assigned before. For example::

	aap
	aap.noot
	aap.noot.mies

Resolving a value is done by looking up the leftmost part in the scope (which
becomes the new scope), then the second-to-left, and so on.

Calling
-------

Calling can be done to defined functions or struct members. Passing them the
correct(!) number of arguments results in executing the function and getting
back its result, or constructing a struct instance and getting that back. If
the number of arguments mismatches, an error occurs. Calling is done using the
``function(arg1, arg2, ...)`` syntax. For example::

	no-arguments()
	some-arguments(namely, these, 3)
	call(with(more.complicated), arguments, "like strings")

First, the expressions for the function and its arguments are evaluated from
left to right, then the call is made. When executing a function, the scope's
parent is the scope where the function was defined. This also implies recursive
calls are possible.

Matching
--------

The most complicated expression is the match expression. This compares a
struct's value with one of several formats, and executes the block of the first
format that corresponds. If no format corresponds, the block after the
``match`` header is executed. For example::

	match to-reverse:
		print("Can't reverse something that isn't a list!")
	case cons-list.empty():
		cons-list.empty()
	case cons-list.cons(`head, `tail):
		append(reverse(tail), head)

If a case or the match header doesn't have a block following it, an error
occurs instead. Note that this means you can't use fallthrough or treat
multiple cases in one block. If Swail did allow you to do this, it would be
very easy to accidentally change only one case without changing the other.
Here's an example of a match expression with empty cases::

	match doesnt-have-one-element
	case cons-list.empty():
		0
	case cons-list.cons(`head, cons-list.empty())
	case cons-list.cons(`head, `tail):
		1 + len(tail)

A format is either a variable or a record. A record has the same basic syntax
as a call to a struct member: a name that resolves to a struct member, and some
arguments that are also formats. A variable is indicated by a ``\``` character
and a name. Using ``\``` for quoting will return later on! A variable format
matches any struct instance. A record format matches an instance if the members
are exactly the same (i.e. are defined in the same place in the same structs)
and if all the arguments to the record match with all the arguments to the
instance.

Decorating
==========

You can also compose the functions involved in declarations, using decorators.
Each declaration can be preceded by one or more decorators. These are functions
that take the constructed value and modify it in some way. This is the feature
used to build more complicated features on top of the simpler built-ins. For
example, a web page that only logged in users can see::

	block check-auth(auth-level):
		user = get-logged-in()
		if not has-auth-level(user, auth-level):
			return error-403()
	
	def require-auth(auth-level):
		def decorator(name, route):
			route(name, [route.url], check-auth(auth-level) <> route.code)
	
	@require-auth(levels.logged-in)
	route hello("/hello"):
		"Hello, World!"

Tests
=====

Static checking is probably the best way to make sure your program does what
you want it to do. However, due to extension-after-the-fact and computability
issues and such, many things are not able to be statically checked. Swail's
tests allow you to do static checking, but also retain safety dynamically.

Let's start with a very simple example::

	def return-four():
		3
	
	test return-four_returns-a-number():
		assert type(return-four()) <= number
	
	test return-four_actually-returns-four():
		assert return-four() == 4
	
	def main():
		print(return-four())

Obviously, we expect the second test to fail, but the first to succeed. When
you fire up your favorite Swail compiler/interpreter, you should see something
along the lines of::

	$ swail return_four.swa
	=== TEST FAILURE ===
	in test 'return_four_actually_returns_four'
	in 'assert return_four() == 4'
	as 'assert 3 == 4'
	as 'assert bool.false()':
		Assertion failed.
	
	Tests failed, compilation stopped.

Even better Swail compilers/interpreters also have a flag that represents more
detailed test output, so you can see that the first test succeeded.

There are more interesting tests, though. For example, you can run tests with
arbitrary input::

	def get-second-item(at-least-two-items):
		match at-least-two-items
		case _ :: second :: _:
			second
	
	test get-second-item-from-at-least-two(first, second, rest : cons-list):
		list-to-test = first :: second :: rest
		assert get-second-item(list-to-test) == second

You can also make tests part of a type class to reflect the type class's laws::

	class monoid(m):
		def empty(m)
		def concat(m -> m -> m)
		
		test empty-is-identity(other : m):
			assert concat(empty, other) == concat(other, empty) == other
		
		test concat-is-associative(a : m, b : m, c : m):
			assert concat(a, concat(b, c)) == concat(concat(a, b), c)

Tests are also used behind-the-scenes to implement types. Compare the
implementation with types::

	@has-type(types.st(`x : types.list(`a), len(`x) >= 2) -> `a)
	def get-second-item-typed(at-least-two-items):
		match at-least-two-items
		case _ :: second :: _:
			second

with this decorator-based implementation::

	@typecheck(typecheck-get-second-item):
	def get-second-item-typed(at-least-two-items):
		match at-least-two-items
		case _ :: second :: _:
			second
	
	test typecheck-get-second-item(function, *args, **kwargs):
		match args
		case [`x]:
			match type(x)
			case types.list(`a):
				assert len(x) >= 2
				result = function(*args, **kwargs)
				match type(result)
				case a:
					result

During testing, when get-second-item is called, the typecheck test will run.
During execution, the implementation defines what gets run, probably based on
the parameters you passed the compiler/interpreter.
