from rpython.rlib.parsing.deterministic import LexerError
from rpython.rlib.parsing.ebnfparse import parse_ebnf, make_parse_function
from rpython.rlib.parsing.parsing import ParseError

from rswail.parser import lexed_to_nodes

import pytest

def test_parser_sanity():
	"""Try making a parser with nested repetition and removing symbols.
	
	The current default version of RPython doesn't like placing a * symbol in []
	but we'd like to use that combination for the newlines between statements
	so we have to make sure the version we're building against does.
	"""
	regexes, rules, ToAST = parse_ebnf("""
		test: ["foo"*] "bar";
	""")
	parse_func = make_parse_function(regexes, rules, eof=True)
	parse_func("bar")
	parse_func("foobar")
	parse_func("foofoofoobar")
	with pytest.raises(ParseError):
		parse_func("foo")
	with pytest.raises(LexerError):
		parse_func("quux")
	with pytest.raises(ParseError):
		parse_func("")

def test_empty_file():
	"""Parsing an empty file should succeed and give an empty program."""
	lexed_to_nodes("\n")

def test_simple_statements():
	"""Parse a few simple statements."""
	statements = [
			# headered
			"foo bar(1)\n",
			"foo FooBar37_Quux(1)\n",
			"foo.bar quux()\n",
			"foo.bar.baz quux()\n",
			"foo.bar quux(arg1, arg2, 3, 4, arg5)\n",
			"foo bar(1, 2)\n",
			# expression
			"1\n",
			"foo()\n",
			"foo.bar()\n",
			"foo.bar(arg1, arg2, 3, 4, arg5)\n",
			"foo(bar(baz), quux)\n",
	]
	for statement in statements:
		lexed_to_nodes(statement)
	lexed_to_nodes("\n".join(statements))

def test_statement_with_block():
	"""Parse statements with a block."""
	statements = [
			"def foo():\n<indent>\tpass\n<dedent>\t\n",
			"def foo():\n<indent>\tdef bar():\n<indent>\tpass\n<dedent>\t<dedent>\t\n"
			"def foo():\n<indent>\tdef bar():\n<indent>\tpass\n<dedent>\t\n<dedent>\t\n"
	]
	for statement in statements:
		lexed_to_nodes(statement)
	lexed_to_nodes("\n".join(statements))
