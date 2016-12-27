class Value:
	"""Swail's base type.
	
	Since Swail is kind of object-oriented, we have a dict with the object's
	attributes.
	Since Swail is kind of declarative, we also remember the object's name as
	given in the declaration.
	"""
	def __init__(self, name):
		self.dict = {}
		self.name = name
		self.set(u"name", name)
	def get(self, key):
		assert isinstance(unicode, key)
		return self.dict[key]
	def set(self, key, value):
		assert isinstance(unicode, key)
		self.key = value
	def eq(self, other):
		"""== operator.
		
		By default, returns whether the references are identical.
		"""
		return self is other

class Integer(Value):
	"""A (long) integer.
	"""
	def __init__(self, value):
		"""Create a new integer from a bigint value."""
		self.value = value
	
	def eq(self, other):
		"""Is this integer equivalent to another?
		
		As a convenience, also supports equivalence to int and bigint.
		"""
		if isinstance(other, Integer):
			return self.value.eq(other.value)
		elif isinstance(other, int):
			return self.value.int_eq(other)
		else:
			return self.value.eq(other)

	def __repr__(self):
		return "<Integer({}) at {}>".format(self.value, id(self))
