from rswail.value import Value

class Instruction:
	"""Contains constants for each instruction in the language."""
	NOP = 0 # Do nothing
	HELLO = 1 # Print "Hello, World!"
	PUSH_INT = 2 # Push pc+1 as Integer
	WRITE = 3 # Pop and print to stdout
	JUMP = 4 # Unconditional, scopeless jump to block pc+1
	
	HCF = 255 # Halt and Catch Fire: should never be implemented

"""Maps human-readable instruction names to instruction ids."""
instruction_names = {
		"nop": Instruction.NOP,
		"hello": Instruction.HELLO,
		"push_int": Instruction.PUSH_INT,
		"write": Instruction.WRITE,
		"jump": Instruction.JUMP,
		
		"hcf": Instruction.HCF,
}

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
		self.blocks.append([])
		return len(self.blocks) - 1

	def add_instruction(self, block_id, instruction):
		"""Add an instruction to the end of the given block.
		
		The block must have been initialized (e.g. using self.new_block).
		"""
		self.blocks[block_id].append(instruction)

	def get_block(self, block_id):
		"""Get all instructions in the given block."""
		return self.blocks[block_id]
