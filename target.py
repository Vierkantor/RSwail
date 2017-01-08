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

from rswail.ast import Closure, compile_statement
from rswail.bytecode import Program
from rswail.cons_list import to_list
from rswail.execute import main_loop
from rswail.globals import make_globals
from rswail.parser import swail_parser

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

def start_execution(program, stack=None):
	"""Run the program from its starting block.
	
	If the stack isn't left None, it should support .append() and .pop() methods.
	(e.g. a regular Python list would work)
	
	Returns the stack after execution.
	"""
	if stack is None:
		stack = []
	# TODO: distinguish between these things
	local_vars = make_globals()
	return main_loop(program, program.start_block, stack, local_vars)

def run(fp):
	program_contents = ""
	while True:
		read = os.read(fp, 4096)
		if len(read) == 0:
			break
		program_contents += read
	os.close(fp)
	program = parse(program_contents)
	start_execution(program)

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
