from rpython.rlib.jit import JitDriver, hint
from rpython.rlib.rbigint import rbigint

from rswail.bytecode import Instruction
from rswail.function import Function
from rswail.globals import make_globals
from rswail.value import Integer, Label

jitdriver = JitDriver(greens=['pc', 'block_id', 'scope'],
		reds=['stack', 'frame', 'local_vars', 'program'],
		virtualizables=['frame'],
		is_recursive=True,
		)


def jitpolicy(driver): # pragma: no cover
	from rpython.jit.codewriter.policy import JitPolicy
	return JitPolicy()

class Frame:
	"""Represents the state of execution.
	
	Not to be confused with a closure,
	which represents a set of variables during compilation.
	A closure can cause many stack frames,
	e.g. when a function is called many times.
	"""

	_virtualizable_ = [
			'program',
			'block_id',
			'local_vars',
			'scope',
			'pc',
			'ended',
			'previous_frame',
	]

	_immutable_fields_ = [
			'program',
	]

	def __init__(self, program, block_id, previous_frame=None):
		"""Create a new stack frame.
		
		program is the program we're executing,
		block_id is the block that execution starts at,
		previous_frame is a reference to the frame to return to (if not None).
		"""
		self = hint(self, access_directly=True, fresh_virtualizable=True)
		self.program = program
		self.block_id = block_id
		self.local_vars = make_globals() # TODO: untangle locals and globals

		self.switch_scope()
		self.previous_frame = previous_frame

	def switch_scope(self):
		"""Initialize the scope we just switched to."""
		self.scope = self.program.get_block(self.block_id)
		self.pc = 0
		self.ended = len(self.scope.opcodes) <= self.pc

	def get_opcode(self):
		"""Get the opcode of the instruction that will be executed."""
		return self.scope.opcodes[self.pc]
	def get_argument(self):
		"""Get the argument to the instruction that will be executed."""
		return self.scope.arguments[self.pc]
	def next_instruction(self):
		"""Mark the instruction as executed and fetch the next one."""
		self.pc += 1
		if len(self.scope.opcodes) <= self.pc:
			self.ended = True

	def jump_label(self, argument):
		"""Go to the block after looking up its label."""
		assert argument >= 0
		block_id = self.scope.labels[argument]
		self.jump_id(block_id)

	def jump_id(self, block_id):
		"""Go to the block with the given id."""
		assert isinstance(block_id, int)
		self.block_id = block_id
		self.switch_scope()

	def get_constant(self, constant_id):
		"""Get the constant with given id from the scope."""
		return self.scope.constants[constant_id]
	def get_name(self, name_id):
		"""Get the name with given id from the scope."""
		return self.scope.names[name_id]
	def next_block_id(self):
		"""Get the block id to jump to from the scope.
		
		Execution will go to this block after the current block finishes.
		"""
		return self.scope.next_block_id

def main_loop(program, block_id, stack):
	frame = Frame(program, block_id)
	del program
	del block_id
	while True:
		# tell JIT that we've merged multiple execution flows
		jitdriver.jit_merge_point(program=frame.program, scope=frame.scope,
				local_vars=frame.local_vars, pc=frame.pc, block_id=frame.block_id,
				stack=stack, frame=frame)

		if frame.ended:
			break
		opcode = frame.get_opcode()
		argument = frame.get_argument()
		if opcode == Instruction.NOP:
			pass
		elif opcode == Instruction.HELLO:
			print("Hello, World!")
		elif opcode == Instruction.PUSH_INT:
			stack.append(Integer(rbigint.fromint(argument)))
		elif opcode == Instruction.WRITE:
			print(stack.pop())
		elif opcode == Instruction.JUMP:
			frame.jump_label(argument)
			jitdriver.can_enter_jit(program=frame.program, scope=frame.scope,
				local_vars=frame.local_vars, pc=frame.pc, block_id=frame.block_id,
				stack=stack, frame=frame)
			# don't increment the program counter!
			continue
		elif opcode == Instruction.JUMP_IF:
			tos = stack.pop()
			if tos.bool():
				frame.jump_label(argument)
				jitdriver.can_enter_jit(program=frame.program, scope=frame.scope,
					local_vars=frame.local_vars, pc=frame.pc, block_id=frame.block_id,
					stack=stack, frame=frame)
				# don't increment the program counter!
				continue
		elif opcode == Instruction.JUMP_LABEL:
			assert 0 < argument <= len(stack)
			block_label = stack.pop(-argument)
			assert isinstance(block_label, Label)
			frame.jump_id(block_label.get_value())
			jitdriver.can_enter_jit(program=frame.program, scope=frame.scope,
				local_vars=frame.local_vars, pc=frame.pc, block_id=frame.block_id,
				stack=stack, frame=frame)
			# don't increment the program counter!
			continue
		elif opcode == Instruction.PUSH_CONST:
			stack.append(frame.get_constant(argument))
		elif opcode == Instruction.LOAD_LOCAL:
			name = frame.get_name(argument)
			assert isinstance(name, unicode)
			stack.append(frame.local_vars[name])
		elif opcode == Instruction.STORE_LOCAL:
			name = frame.get_name(argument)
			assert isinstance(name, unicode)
			frame.local_vars[name] = stack.pop()
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
			assert 0 < argument <= len(stack)
			stack.append(stack[-argument])
		elif opcode == Instruction.SWAP:
			assert 0 < argument <= len(stack)
			stack.append(stack.pop(-argument))
		elif opcode == Instruction.CALL:
			function_pos = len(stack) - argument - 1
			assert 0 <= function_pos < len(stack)
			function = stack[function_pos]
			assert isinstance(function, Function)
			return_id = frame.next_block_id()
			new_frame, next_block = function.call(return_id, stack, function_pos)
			if new_frame:
				# TODO: the JIT doesn't like the frame being replaced
				# so figure out some way to not replace it?
				# TODO: this is a hacky way to get globals into scope
				frame = Frame(frame.program, next_block, frame)
			else:
				frame.jump_id(next_block)
			continue
		else:
			raise NotImplementedError
		frame.next_instruction()
	return stack
