#!/usr/bin/env python2

import pytest

from rswail.ast import compile_expression, expr_base_value
from rswail.bytecode import Program
from rswail.value import Integer
from target import mainloop

def test_base_value():
	"""Load a base value in an expression."""
	program = Program()
	expr = expr_base_value(Integer.from_int(37))
	compile_expression(program, program.start_block, expr)

	stack = mainloop(program)

	tos = stack[-1]
	assert tos.eq(37)
