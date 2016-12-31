from rswail.value import Value

class Function(Value):
	"""Base class for functions."""
	def __init__(self, name):
		Value.__init__(self, name)
	
	def call(self, arguments):
		"""Call the function with a tuple of arguments.
		
		Returns a single Value.
		"""
		raise Exception("call to abstract method Function.call")

class NativeFunction(Function):
	"""Built-in function written in native code."""
	def __init__(self, name, func):
		Value.__init__(self, name)
		self.func = func
		self.set(u"func", self.func)
	
	def call(self, arguments):
		return self.func(arguments)
