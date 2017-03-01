class Closure:
	"""Represents a set of variables during compilation.
	
	Not to be confused with a stack frame,
	which represents a set of variables during execution.
	A closure can cause many stack frames,
	e.g. when a function is called many times.
	"""
	def __init__(self):
		"""Make a new closure."""
		
		"""The variables bound in this closure.
		
		We need to track these variables so we can load them from the
		appropriate stack frame whenever they're used.
		
		Since RPython doesn't support sets, we make this a dict {key: None}
		"""
		self.bound_variables = {}
		"""The free variables in this closure which will need to be bound.
		
		We need to track these variables so we can load them from the
		appropriate stack frame.
		
		Note that bound_variables and used_variables can have any kind of overlap.
		"""
		self.used_variables = {}
	def make_bound(self, name):
		"""Remember that a declaration introduces a new name."""
		assert isinstance(name, unicode)
		self.bound_variables[name] = None
	def make_used(self, name):
		"""Remember that an expression wants to load a variable.
		"""
		assert isinstance(name, unicode)
		self.used_variables[name] = None
	def get_free_variables(self):
		"""Calculate which variables need to be closed over in the outer frame.
		
		Returns a dict {variable: None} since RPython has no sets.
		"""
		result = {}
		for key in self.used_variables:
			if key not in self.bound_variables:
				result[key] = None
		return result

