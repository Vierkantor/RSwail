#!/usr/bin/env python2

import pytest

from rswail.bytecode import Instruction, Program
from target import mainloop

def test_empty_program():
	"""The main loop should accept empty programs."""
	mainloop(Program())

def test_hello_instr(capsys):
	"""The hello world instruction should output exactly this string:
		u"Hello, World!\n"
	"""
	program = Program()
	program.add_instruction(program.start_block, Instruction.HELLO)

	mainloop(program)
	out, err = capsys.readouterr()
	assert out == u"Hello, World!\n"

def test_push_int_instr():
	"""Pushing an int should make the TOS a Swail integer."""
	program = Program()
	program.add_instruction(program.start_block, Instruction.PUSH_INT)
	program.add_instruction(program.start_block, 37)

	stack = mainloop(program)

	tos = stack[-1]
	assert tos.eq(37)

def test_invalid_instr():
	"""We should get an error when an invalid instruction is executed."""
	program = Program()
	program.add_instruction(program.start_block, Instruction.HCF)

	with pytest.raises(NotImplementedError):
		mainloop(program)
