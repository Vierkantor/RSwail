from rpython.rtyper.lltypesystem.lltype import Array, Unsigned

from rswail.closure import Closure
from rswail.value import Unit, Value

class Instruction:
	"""Contains constants for each opcode in the language.
	
	An instruction consists of an opcode and one argument.
	The opcode determines what to do, the argument how to do it.
	For example, PUSH_INT takes an int as argument and places it on the stack.
	If the description doesn't mention its meaning, the argument is any valid value.
	
	TODO: decide how many bits we want to use for opcodes / arguments.
	"""
	NOP = 0 # Do nothing
	HELLO = 1 # Print "Hello, World!"
	PUSH_INT = 2 # Push <arg> as Integer
	WRITE = 3 # Pop and print to stdout
	JUMP = 4 # Unconditional, scopeless jump to block <arg>
	JUMP_IF = 5 # Pop, if truthy then JUMP else NOP
	PUSH_CONST = 6 # Push constants[<arg>]
	LOAD_LOCAL = 7 # Push locals[names[<arg>]]
	STORE_LOCAL = 8 # Pop and write to locals[names[<arg>]]
	POP = 9 # Pop <arg> values from the stack (0 < arg)
	DUP = 10 # Duplicate the <arg>th value on the stack (0 < arg <= len(stack))
	CALL = 11 # Pop <arg> arguments, pop function, call function with arguments
	LOAD_ATTR = 12 # Pop value and push value[names[<arg>]]
	JUMP_LABEL = 13 # Pop <arg>th value on the stack and jump to the labeled block
	SWAP = 14 # Move the <arg>th value on the stack to TOS (0 < arg <= len(stack))
	
	HCF = 255 # Halt and Catch Fire: should never be implemented

"""Maps human-readable instruction names to instruction ids."""
instruction_names = {
		"nop": Instruction.NOP,
		"hello": Instruction.HELLO,
		"push_int": Instruction.PUSH_INT,
		"write": Instruction.WRITE,
		"jump": Instruction.JUMP,
		"jump_if": Instruction.JUMP_IF,
		"push_const": Instruction.PUSH_CONST,
		"load_local": Instruction.LOAD_LOCAL,
		"store_local": Instruction.STORE_LOCAL,
		"pop": Instruction.POP,
		"dup": Instruction.DUP,
		"call": Instruction.CALL,
		"load_attr": Instruction.LOAD_ATTR,
		"jump_label": Instruction.JUMP_LABEL,
		"swap": Instruction.SWAP,
		
		"hcf": Instruction.HCF,
}

class TooManyItemsError(Exception):
	"""Raised when a block contains too many local items, e.g. labels."""
	pass

"""An invalid block id.

Whenever a jump is executed to this block id, an error occurs.
Flags cases like returning in a block that doesn't expect return values.
"""
INVALID_BLOCK = -1

class Block:
	"""The smallest grouping of code, with labels and constants."""
	def __init__(self):
		"""Make a new empty block."""
		
		"""The opcodes of the instructions in the program.
		
		Should contain exactly as many items as self.arguments
		"""
		self.opcodes = []
		
		"""The arguments of the instructions in the program.
		
		Should contain exactly as many items as self.opcodes
		"""
		self.arguments = []
		
		"""The jump labels (i.e. block ids) used in this block.
		
		Every label should be used for an instruction.
		"""
		self.labels = [0] # TODO: better type hinting
		
		"""The constants (i.e. values that don't reference other values) used
		in this block.
		
		Every constant should be used for an instruction.
		"""
		self.constants = [Unit()] # TODO: better type hinting
		
		"""The names (i.e. unicode strings) used in this block.
		
		Each name should be used for an instruction.
		"""
		self.names = [u''] # TODO: better type hinting
		
		"""The block id to jump to after this block finishes execution."""
		self.next_block_id = INVALID_BLOCK # TODO: better type hinting
	
	def add_constant(self, value):
		"""Add a constant to this block.
		
		Returns the id of the constant.
		"""
		assert isinstance(value, Value)
		self.constants.append(value)
		return len(self.constants) - 1
	
	def add_instruction(self, opcode, argument):
		"""Add an instruction to the end of this block."""
		assert isinstance(opcode, int)
		assert isinstance(argument, int)
		self.opcodes.append(opcode)
		self.arguments.append(argument)
	
	def add_label(self, label):
		"""Add a label to this block.
		
		Returns the id of this label.
		"""
		assert isinstance(label, int)
		self.labels.append(label)
		return len(self.labels) - 1
	
	def add_name(self, name):
		"""Add a name to this block.
		
		Returns the id of the name.
		"""
		assert isinstance(name, unicode)
		# don't waste too much space on non-unique names
		if name in self.names:
			return self.names.index(name)
		self.names.append(name)
		return len(self.names) - 1

	def pretty_print(self): # pragma: no cover
		"""Format this object into a human-readable (python) string."""
		return u"block {}".format(list(zip(self.opcodes, self.arguments)))

class Program:
	"""Defines the full program, with blocks and initialization."""
	def __init__(self):
		"""Make a new empty program."""
		
		"""Contains the code in the program.
		
		Jump instructions always go to the start of a block.
		"""
		self.blocks = []
		"""By default, a single block numbered start_block has been initialized.
		
		This block is the one the main loop starts off executing, so it's useful
		for writing program initialization code and other static stuff.
		"""
		self.start_block = self.new_block()

	def new_block(self):
		"""Make a new block and give its id."""
		self.blocks.append(Block())
		return len(self.blocks) - 1

	def add_constant(self, block_id, value):
		return self.blocks[block_id].add_constant(value)

	def add_instruction(self, block_id, opcode, argument=0):
		"""Add an instruction to the end of the given block.
		
		The block must have been initialized (e.g. using self.new_block).
		
		You should leave the argument empty only when the instruction doesn't
		take an argument.
		"""
		return self.blocks[block_id].add_instruction(opcode, argument)

	def add_label(self, block_id, label):
		"""Add a label to the given block."""
		return self.blocks[block_id].add_label(label)

	def add_name(self, block_id, name):
		"""Add a name to the given block."""
		return self.blocks[block_id].add_name(name)

	def get_block(self, block_id):
		"""Get the block object from its id."""
		return self.blocks[block_id]

	def set_next_block_id(self, block_id, next_block_id):
		"""Set the block id to jump to after this block finishes execution."""
		self.blocks[block_id].next_block_id = next_block_id
	
	def make_next_block(self, block_id):
		"""Go to a new block after the given one finishes.
		
		Makes a new block and sets the next block id.
		Returns the id of the newly created block.
		"""
		next_block_id = self.new_block()
		self.set_next_block_id(block_id, next_block_id)
		return next_block_id
