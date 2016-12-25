#!/usr/bin/env python2

import os
import sys

from rpython.rlib.jit import JitDriver

# TODO: make this nicer, via namespaces maybe?
INSTR_NOP = 0 # Do nothing
INSTR_HELLO = 1 # Hello, World!

word_to_instruction = {
	"nop": INSTR_NOP,
	"hello": INSTR_HELLO,
}

jitdriver = JitDriver(greens=['pc', 'program', 'extras'],
		reds=['stack'])
def jitpolicy(driver):
	from rpython.jit.codewriter.policy import JitPolicy
	return JitPolicy()

class ProgramExtras:
	def __init__(self):
		pass

def parse(program_contents):
	program = []
	extras = ProgramExtras()
	for line in program_contents.split("\n"):
		if line:
			program.append(word_to_instruction[line])
	return program, extras

def mainloop(program, extras):
	stack = []
	pc = 0
	while pc < len(program):
		# tell JIT that we've merged multiple execution flows
		jitdriver.jit_merge_point(pc=pc, program=program, extras=extras,
				stack=stack)

		instruction = program[pc]
		if instruction == INSTR_NOP:
			pass
		elif instruction == INSTR_HELLO:
			print("Hello, World!")
		else:
			raise NotImplementedError
		pc += 1

def run(fp):
	program_contents = ""
	while True:
		read = os.read(fp, 4096)
		if len(read) == 0:
			break
		program_contents += read
	os.close(fp)
	program, extras = parse(program_contents)
	mainloop(program, extras)

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
