#!/usr/bin/env python2

"""
	RSwail - A RPython-based implementation of the Swail language.
	
	This program is free software: you can redistribute it and/or modify it
	under the terms of the GNU General Public License as published by the Free
	Software Foundation, either version 3 of the License, or (at your option)
	any later version.

	This program is distributed in the hope that it will be useful, but WITHOUT
	ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
	FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
	more details.

	You should have received a copy of the GNU General Public License along
	with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys

# TODO: we should be able to do this better
# e.g. without manipulating the python path
sys.path.append("pypy")
from rpython.rlib.jit import JitDriver
from rpython.rlib.rbigint import rbigint

from rswail.ast import Closure, compile_statement
from rswail.bytecode import Instruction, Program, instruction_names
from rswail.cons_list import to_list
from rswail.function import Function
from rswail.globals import make_globals
from rswail.parser import swail_parser
from rswail.value import Integer

jitdriver = JitDriver(greens=['pc', 'program', 'scope'],
		reds=['stack', 'local_vars'])

def jitpolicy(driver): # pragma: no cover
	from rpython.jit.codewriter.policy import JitPolicy
	return JitPolicy()

def parse(program_contents):
	# parse the program
	parsed = swail_parser(program_contents)

	# compile the program
	program = Program()
	block_id = program.start_block
	globals = Closure()
	for statement in to_list(parsed):
		block_id = compile_statement(program, block_id, statement, globals)
	return program

def mainloop(program, stack=None):
	"""Run the program from its starting block.
	
	If the stack isn't left None, it should support .append() and .pop() methods.
	(e.g. a regular Python list would work)
	
	Returns the stack after execution.
	"""
	if stack is None:
		stack = []
	# TODO: distinguish between these things
	local_vars = make_globals()
	pc = 0
	scope = program.get_block(program.start_block)
	while pc < len(scope.opcodes):
		# tell JIT that we've merged multiple execution flows
		jitdriver.jit_merge_point(program=program, scope=scope, pc=pc,
				stack=stack, local_vars=local_vars)

		opcode = scope.opcodes[pc]
		argument = scope.arguments[pc]
		if opcode == Instruction.NOP:
			pass
		elif opcode == Instruction.HELLO:
			print("Hello, World!")
		elif opcode == Instruction.PUSH_INT:
			stack.append(Integer(rbigint.fromint(argument)))
		elif opcode == Instruction.WRITE:
			print(stack.pop())
		elif opcode == Instruction.JUMP:
			assert argument >= 0
			label = scope.labels[argument]
			assert isinstance(label, int)
			scope = program.get_block(label)
			pc = 0
			# don't increment the program counter!
			continue
		elif opcode == Instruction.JUMP_IF:
			tos = stack.pop()
			assert argument >= 0
			if tos.bool():
				label = scope.labels[argument]
				assert isinstance(label, int)
				scope = program.get_block(label)
				pc = 0
				# don't increment the program counter!
				continue
		elif opcode == Instruction.PUSH_CONST:
			stack.append(scope.constants[argument])
		elif opcode == Instruction.LOAD_LOCAL:
			name = scope.names[argument]
			assert isinstance(name, unicode)
			stack.append(local_vars[name])
		elif opcode == Instruction.STORE_LOCAL:
			name = scope.names[argument]
			assert isinstance(name, unicode)
			local_vars[name] = stack.pop()
		elif opcode == Instruction.POP:
			if argument >= len(stack):
				stack = []
			else:
				new_length = len(stack) - argument
				# help rpython out with basic arithmetic
				# so it knows the stack is nonempty
				assert new_length > 0
				stack = stack[:new_length]
		elif opcode == Instruction.DUP:
			assert 0 < argument < len(stack)
			stack.append(stack[-argument])
		elif opcode == Instruction.CALL:
			function_pos = len(stack) - argument - 1
			assert 0 <= function_pos < len(stack)
			function = stack[function_pos]
			arguments = stack[function_pos+1:]
			stack = stack[:function_pos]
			assert isinstance(function, Function)
			stack.append(function.call(arguments))
		else:
			raise NotImplementedError
		pc += 1
	return stack

def run(fp):
	program_contents = ""
	while True:
		read = os.read(fp, 4096)
		if len(read) == 0:
			break
		program_contents += read
	os.close(fp)
	program = parse(program_contents)
	mainloop(program)

def entry_point(argv):
	try:
		filename = argv[1]
	except IndexError:
		print("You must supply a filename")
		return 1

	run(os.open(filename, os.O_RDONLY, 0777))
	return 0

def target(*args):
	return entry_point, None

if __name__ == "__main__":
	entry_point(sys.argv)
