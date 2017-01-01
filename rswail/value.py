from rpython.rlib.rbigint import rbigint

class Value:
	"""Swail's base type.
	
	Since Swail is kind of object-oriented, we have a dict with the object's
	attributes.
	Since Swail is kind of declarative, we also remember the object's name as
	given in the declaration.
	"""
	def __init__(self, name):
		assert isinstance(name, unicode)
		self.dict = {}
		self.name = name
		self.set(u"name", name)
	def get(self, key):
		assert isinstance(key, unicode)
		return self.dict[key]
	def set(self, key, value):
		assert isinstance(key, unicode)
		self.key = value
	def bool(self):
		"""bool operator.
		
		Convert the value to a boolean.
		Zero or empty values give false, nonzero or nonempty values give true.
		
		As with all operators, returns a native value.
		"""
		return True
	def eq(self, other):
		"""== operator.
		
		By default, returns whether the references are identical.
		
		As with all operators, returns a native value.
		"""
		return self is other

class Unit(Value):
	"""The unit value, of which there is exactly one."""
	def __init__(self):
		Value.__init__(self, u'()')

	def bool(self):
		return False

	def eq(self, other):
		return isinstance(other, Unit)

class Boolean(Value):
	"""A boolean value, either True or False."""
	def __init__(self, value):
		assert isinstance(value, bool)

		Value.__init__(self, unicode(str(value)))
		self.value = value

	def bool(self):
		return self.value

class Integer(Value):
	"""A (long) integer."""
	def __init__(self, value):
		"""Create a new integer from a bigint value."""
		assert isinstance(value, rbigint)

		Value.__init__(self, unicode(value.str()))
		self.value = value

	@classmethod
	def from_int(self, value):
		return Integer(rbigint.fromint(value))

	@classmethod
	def from_decimal(self, value):
		return Integer(rbigint.fromdecimalstr(value))

	def bool(self):
		"""Convert integer to boolean.
		
		Nonzero values are True, zero values are False.
		"""
		return not self.value.int_eq(0)

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

	def __unicode__(self):
		return u"<Integer({}) at {}>".format(self.value, id(self))
