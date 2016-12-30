#!/usr/bin/env python2

import os
import sys

sys.path.append("pypy")
from rpython.rlib.jit import JitDriver
from rpython.rlib.rbigint import rbigint

from rswail.bytecode import Instruction, Program, instruction_names
from rswail.value import Integer

jitdriver = JitDriver(greens=['pc', 'program', 'scope'],
		reds=['stack', 'local_vars'])
def jitpolicy(driver):
	from rpython.jit.codewriter.policy import JitPolicy
	return JitPolicy()

class ProgramExtras:
	def __init__(self):
		pass

def parse(program_contents):
	program = Program()
	current_block = program.start_block
	for line in program_contents.split("\n"):
		if line:
			instruction, argument = line.split(" ")
			program.add_instruction(current_block,
					instruction_names[instruction],
					int(argument),
			)
	return program

def mainloop(program, stack=None):
	if stack is None:
		stack = []
	local_vars = {}
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
