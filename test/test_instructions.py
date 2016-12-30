#!/usr/bin/env python2

import pytest

from rswail.bytecode import Instruction, Program
from rswail.value import Integer
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
	# push an arbitrary integer
	program.add_instruction(program.start_block, Instruction.PUSH_INT, 37)

	stack = mainloop(program)

	tos = stack[-1]
	assert tos.eq(37)

def test_invalid_instr():
	"""We should get an error when an invalid instruction is executed."""
	program = Program()
	program.add_instruction(program.start_block, Instruction.HCF)

	with pytest.raises(NotImplementedError):
		mainloop(program)

def test_jump_instr():
	"""Jump to another part in the code."""
	program = Program()
	block1 = program.start_block
	block2 = program.new_block()
	label1 = program.add_label(block1, block2)
	# go to the other block
	program.add_instruction(block1, Instruction.JUMP, label1)
	# and push an int
	program.add_instruction(block2, Instruction.PUSH_INT, 37)

	stack = mainloop(program)

	tos = stack[-1]
	assert tos.eq(37)

def test_jump_if_instr():
	"""Don't jump if there's a 0 and jump if there's a 1."""
	program = Program()
	block1 = program.start_block
	block2 = program.new_block()
	block3 = program.new_block()
	label1_2 = program.add_label(block1, block2)
	label1_3 = program.add_label(block1, block3)
	# Since we push 1 first, we'll jump second
	program.add_instruction(block1, Instruction.PUSH_INT, 1)
	program.add_instruction(block1, Instruction.PUSH_INT, 0)
	program.add_instruction(block1, Instruction.JUMP_IF, label1_2)
	program.add_instruction(block1, Instruction.JUMP_IF, label1_3)
	# mark where we've ended up
	program.add_instruction(block2, Instruction.PUSH_INT, 2)
	program.add_instruction(block3, Instruction.PUSH_INT, 3)

	stack = mainloop(program)

	tos = stack[-1]
	assert tos.eq(3)

def test_load_const_instr():
	"""Pushing a local constant should be equivalent to pushing an int."""
	program = Program()
	const = program.add_constant(program.start_block, Integer.from_int(37))
	program.add_instruction(program.start_block, Instruction.PUSH_CONST, const)
	program.add_instruction(program.start_block, Instruction.PUSH_INT, 37)

	stack = mainloop(program)

	tos = stack[-1]
	sos = stack[-2]
	assert tos.eq(sos)

def test_store_load_local():
	"""Storing and loading a local value should do nothing."""
	program = Program()
	program.add_instruction(program.start_block, Instruction.PUSH_INT, 37)
	var_id = program.add_name(program.start_block, u"var")
	program.add_instruction(program.start_block, Instruction.STORE_LOCAL, var_id)
	program.add_instruction(program.start_block, Instruction.LOAD_LOCAL, var_id)

	stack = mainloop(program)

	tos = stack[-1]
	assert tos.eq(37)
