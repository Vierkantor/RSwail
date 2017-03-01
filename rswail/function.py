from rswail.value import Label, Value

class Function(Value):
	"""Base class for functions."""
	def __init__(self, name):
		Value.__init__(self, name)
	
	def call(self, return_id, stack, arg_start): # pragma: no cover
		"""Call the function with some arguments.
		
		return_id is the id of the block that will handle the return value.
		stack is the value stack at the time of calling,
		stack[arg_start+1:] is the list of arguments to the function.
		
		You may write to stack[arg_start:] e.g. for return values.
		After jumping to return_id, TOS must be stack[arg_start],
		which is considered the return value of the function.
		
		Returns whether we need a new stack frame,
		and the block that execution will go to.
		This block should eventually jump to block return_id.
		"""
		raise Exception("call to abstract method Function.call")

class NativeFunction(Function):
	"""Built-in function written in native code."""
	def __init__(self, name, func):
		Function.__init__(self, name)
		self.func = func
	
	def call(self, return_id, stack, arg_start):
		arguments = stack[arg_start+1:]
		stack[arg_start] = self.func(arguments)
		# TODO: this should be nicer!
		for i in range(arg_start+1, len(stack)):
			stack.pop()
		return False, return_id

class CodeFunction(Function):
	"""A function written in bytecode.
	
	When the function is called, all the arguments are on the stack,
	with the last argument as TOS.
	Below the arguments is the label to jump to.
	"""
	def __init__(self, name, block_id):
		Function.__init__(self, name)
		self.block_id = block_id

	def call(self, return_id, stack, arg_start):
		assert isinstance(return_id, int)
		assert isinstance(stack, list)
		assert isinstance(arg_start, int)
		assert 0 <= arg_start < len(stack)
		stack[arg_start] = Label(return_id)
		return True, self.block_id
