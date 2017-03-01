#!/usr/bin/env python2

import pytest

from rswail.bytecode import Instruction, Program
from rswail.function import NativeFunction
from rswail.value import Integer
from target import start_execution

def test_empty_program():
	"""The main loop should accept empty programs."""
	start_execution(Program())

def test_nop_program():
	"""A program with a NOP instruction should also work."""
	program = Program()
	program.add_instruction(program.start_block, Instruction.NOP)
	start_execution(program)

def test_hello_instr(capsys):
	"""The hello world instruction should output exactly this string:
		u"Hello, World!\n"
	"""
	program = Program()
	program.add_instruction(program.start_block, Instruction.HELLO)

	start_execution(program)
	out, err = capsys.readouterr()
	assert out == u"Hello, World!\n"

def test_push_int_instr():
	"""Pushing an int should make the TOS a Swail integer."""
	program = Program()
	# push an arbitrary integer
	program.add_instruction(program.start_block, Instruction.PUSH_INT, 37)

	stack = start_execution(program)

	tos = stack[-1]
	assert tos.eq(37)

def test_invalid_instr():
	"""We should get an error when an invalid instruction is executed."""
	program = Program()
	program.add_instruction(program.start_block, Instruction.HCF)

	with pytest.raises(NotImplementedError):
		start_execution(program)

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

	stack = start_execution(program)

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
	program.add_instruction(block1, Instruction.JUMP_IF, label1_2)
	program.add_instruction(block1, Instruction.JUMP_IF, label1_3)
	# mark where we've ended up
	program.add_instruction(block2, Instruction.PUSH_INT, 2)
	program.add_instruction(block3, Instruction.PUSH_INT, 3)

	# Since 0 is on top, we jump second.
	stack = start_execution(program, [Integer.from_int(1), Integer.from_int(0)])

	tos = stack[-1]
	assert tos.eq(3)

def test_push_const_instr():
	"""Push an integer on the stack as a local constant.
	
	Checks that this is equivalent to already having it on the stack, and
	to directly pushing it onto the stack.
	"""
	program = Program()
	const = program.add_constant(program.start_block, Integer.from_int(37))
	program.add_instruction(program.start_block, Instruction.PUSH_CONST, const)
	program.add_instruction(program.start_block, Instruction.PUSH_INT, 37)

	stack = start_execution(program, [Integer.from_int(37)])

	tos = stack[-1]
	sos = stack[-2]
	dos = stack[-3]
	assert tos.eq(sos)
	assert tos.eq(dos)

def test_write_instr(capsys):
	"""Test that writing the TOS to stdout works."""
	program = Program()
	value = Integer.from_int(37)
	const = program.add_constant(program.start_block, value)
	program.add_instruction(program.start_block, Instruction.PUSH_CONST, const)
	program.add_instruction(program.start_block, Instruction.WRITE)

	start_execution(program)
	out, err = capsys.readouterr()
	# we should get a representation of the int and a newline
	assert out == repr(value) + "\n"


def test_store_load_local():
	"""Storing and loading a local value should do nothing."""
	program = Program()
	var_id = program.add_name(program.start_block, u"var")
	program.add_instruction(program.start_block, Instruction.STORE_LOCAL, var_id)
	program.add_instruction(program.start_block, Instruction.LOAD_LOCAL, var_id)

	stack = start_execution(program, [Integer.from_int(37)])

	tos = stack[-1]
	assert tos.eq(37)

def test_pop_single():
	"""Pop a single value from the stack."""
	program = Program()
	program.add_instruction(program.start_block, Instruction.POP, 1)

	stack = start_execution(program, [Integer.from_int(1), Integer.from_int(2)])
	tos = stack[-1]

	assert tos.eq(1)

def test_pop_multiple():
	"""Pop multiple values from the stack."""
	program = Program()
	program.add_instruction(program.start_block, Instruction.POP, 4)

	stack = []
	for i in range(1, 7):
		stack.append(Integer.from_int(i))

	stack = start_execution(program, stack)
	tos = stack[-1]

	# 1 2 3 4 5 6 -> 1 2
	assert tos.eq(2)

def test_pop_overflow():
	"""Popping more values than the stack contains should give an empty stack."""
	program = Program()
	program.add_instruction(program.start_block, Instruction.POP, 4)

	stack = start_execution(program, [Integer.from_int(1), Integer.from_int(2)])

	assert len(stack) == 0

def test_dup_top():
	"""Duplicate the top value on the stack."""
	program = Program()
	program.add_instruction(program.start_block, Instruction.DUP, 1)

	stack = start_execution(program, [Integer.from_int(1), Integer.from_int(2)])
	tos = stack[-1]
	sos = stack[-2]

	assert tos.eq(2)
	assert sos.eq(2)

def test_dup_deeper():
	"""Duplicate a value which is stored deeper in the stack."""
	program = Program()
	program.add_instruction(program.start_block, Instruction.DUP, 4)

	stack = []
	for i in range(1, 7):
		stack.append(Integer.from_int(i))

	stack = start_execution(program, stack)

	for i, n in enumerate([1, 2, 3, 4, 5, 6, 3]):
		assert stack[i].eq(n)

def test_dup_bottom():
	"""Duplicate a value which is stored on the bottom of the stack."""
	program = Program()
	program.add_instruction(program.start_block, Instruction.DUP, 6)

	stack = []
	for i in range(1, 7):
		stack.append(Integer.from_int(i))

	stack = start_execution(program, stack)

	for i, n in enumerate([1, 2, 3, 4, 5, 6, 1]):
		assert stack[i].eq(n)

def test_swap_top():
	"""Swap the top value on the stack."""
	program = Program()
	program.add_instruction(program.start_block, Instruction.SWAP, 1)

	stack = start_execution(program, [Integer.from_int(1), Integer.from_int(2)])
	tos = stack[-1]
	sos = stack[-2]

	assert tos.eq(2)
	assert sos.eq(1)

def test_swap_deeper():
	"""Swap a value which is stored deeper in the stack."""
	program = Program()
	program.add_instruction(program.start_block, Instruction.SWAP, 4)

	stack = []
	for i in range(1, 7):
		stack.append(Integer.from_int(i))

	stack = start_execution(program, stack)

	for i, n in enumerate([1, 2, 4, 5, 6, 3]):
		assert stack[i].eq(n)

def test_swap_bottom():
	"""Swap a value which is stored on the bottom of the stack."""
	program = Program()
	program.add_instruction(program.start_block, Instruction.SWAP, 6)

	stack = []
	for i in range(1, 7):
		stack.append(Integer.from_int(i))

	stack = start_execution(program, stack)

	for i, n in enumerate([2, 3, 4, 5, 6, 1]):
		assert stack[i].eq(n)

def test_call_noargs():
	"""Call a function without any arguments."""
	program = Program()
	block_id = program.start_block

	def func(args):
		assert len(args) == 0
		return Integer.from_int(37)
	func_id = program.add_constant(block_id, NativeFunction(u"func", func))

	program.add_instruction(block_id, Instruction.PUSH_CONST, func_id)
	program.add_instruction(block_id, Instruction.CALL, 0)
	block_id = program.make_next_block(block_id)

	stack = start_execution(program)
	tos = stack[-1]

	assert tos.eq(37)

def test_call_args():
	"""Call a function with a given number of arguments."""
	program = Program()
	block_id = program.start_block

	def func(args):
		assert len(args) == 5
		assert args[0].eq(1)
		assert args[1].eq(2)
		assert args[2].eq(3)
		assert args[3].eq(4)
		assert args[4].eq(5)
		return Integer.from_int(37)
	func_id = program.add_constant(block_id, NativeFunction(u"func", func))

	program.add_instruction(block_id, Instruction.PUSH_INT, 6)
	program.add_instruction(block_id, Instruction.PUSH_CONST, func_id)
	program.add_instruction(block_id, Instruction.PUSH_INT, 1)
	program.add_instruction(block_id, Instruction.PUSH_INT, 2)
	program.add_instruction(block_id, Instruction.PUSH_INT, 3)
	program.add_instruction(block_id, Instruction.PUSH_INT, 4)
	program.add_instruction(block_id, Instruction.PUSH_INT, 5)
	program.add_instruction(block_id, Instruction.CALL, 5)
	block_id = program.make_next_block(block_id)

	stack = start_execution(program)
	tos = stack[-1]

	assert tos.eq(37)
