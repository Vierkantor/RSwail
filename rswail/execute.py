from rpython.rlib.jit import JitDriver
from rpython.rlib.rbigint import rbigint

from rswail.bytecode import Instruction
from rswail.function import Function
from rswail.value import Integer

jitdriver = JitDriver(greens=['pc', 'program', 'scope'],
		reds=['stack', 'local_vars'])

def jitpolicy(driver): # pragma: no cover
	from rpython.jit.codewriter.policy import JitPolicy
	return JitPolicy()

def main_loop(program, block_id, stack, local_vars):
	scope = program.get_block(block_id)
	pc = 0
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
