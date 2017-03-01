#!/usr/bin/env python2

import pytest

from rswail.ast import Closure, compile_expression, compile_statement, expr_apply, expr_base_value, expr_from_int, expr_name_access, stmt_declaration, stmt_expression
from rswail.cons_list import empty, from_list, singleton
from rswail.bytecode import Program
from rswail.function import NativeFunction
from rswail.value import Integer, String
from target import start_execution

def test_base_value():
	"""Load a base value in an expression."""
	program = Program()
	expr = expr_base_value(Integer.from_int(37))
	closure = Closure()
	compile_expression(program, program.start_block, expr, closure)

	stack = start_execution(program)

	tos = stack[-1]
	assert tos.eq(37)

def test_function_call():
	"""Call a function in an expression."""
	program = Program()
	def func(args):
		assert len(args) == 5
		assert args[0].eq(1)
		assert args[1].eq(2)
		assert args[2].eq(3)
		assert args[3].eq(4)
		assert args[4].eq(5)
		return Integer.from_int(37)
	func_expr = expr_base_value(NativeFunction(u"func", func))
	call_expr = expr_apply(func_expr, from_list(map(expr_from_int, [1, 2, 3, 4, 5])))
	closure = Closure()
	block_id = compile_expression(program, program.start_block, call_expr, closure)

	stack = start_execution(program)
	tos = stack[-1]

	assert tos.eq(37)

def test_expression_statement():
	"""Compile a statement that returns a base value.
	
	Does basically the same as test_base_value but with a statement.
	"""
	program = Program()
	expr = expr_base_value(Integer.from_int(37))
	stmt = stmt_expression(expr)
	closure = Closure()
	compile_statement(program, program.start_block, stmt, closure)

	stack = start_execution(program)

	tos = stack[-1]
	assert tos.eq(37)

def test_declare_and_load():
	"""Declare a function foo and load it in an expression.
	
	Verify that `def is a free variable and `foo is a bound variable.
	"""
	program = Program()
	decl = stmt_declaration(singleton(String(u"def")), String(u"foo"), empty(), empty())
	expr = expr_name_access(singleton(String(u"foo")))
	closure = Closure()
	block_id = compile_statement(program, program.start_block, decl, closure)
	block_id = compile_statement(program, block_id, stmt_expression(expr), closure)

	assert sorted(closure.bound_variables.keys()) == [u"foo"]
	assert sorted(closure.used_variables.keys()) == [u"def", u"foo"]
	assert sorted(closure.get_free_variables().keys()) == [u"def"]

	# TODO: check the program works

def test_load_general_name():
	"""Compile an expression that loads from a name.with.attributes."""
	program = Program()
	expr = expr_name_access(from_list([String(u"foo"), String(u"bar"), String(u"baz")]))
	closure = Closure()
	block_id = program.start_block
	block_id = compile_statement(program, block_id, stmt_expression(expr), closure)

	assert sorted(closure.used_variables.keys()) == [u"foo"]
	assert sorted(closure.get_free_variables().keys()) == [u"foo"]

	# TODO: check the program works
