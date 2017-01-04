from rpython.rlib.objectmodel import not_rpython
from rpython.rlib.rbigint import rbigint

"""When set to True, built-in Python operators on Values will raise.

We enable this during pytest runs to make sure operators don't accidentally
get overloaded in Python and fail in RPython.
"""
_strict_operators = False

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
	def get(self, key):
		assert isinstance(key, unicode)
		if key == u"name" and key not in self.dict:
			return self.name
		return self.dict[key]
	def set(self, key, value):
		assert isinstance(key, unicode)
		assert isinstance(value, Value)
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

	@not_rpython
	def __eq__(self, other):
		"""Throws an error.
		
		RPython doesn't support overriding the == operator,
		so we should catch any accidental usage in the test cases.
		"""
		if _strict_operators:
			raise Exception("using the == operator on objects: use .eq or is")
		else:
			return NotImplemented
	@not_rpython
	def __ne__(self, other):
		"""Throws an error during testing.
		
		RPython doesn't support overriding the != operator,
		so we should catch any accidental usage in the test cases.
		"""
		if _strict_operators:
			raise Exception("using the != operator on objects: use .eq or is")
		else:
			return NotImplemented

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

	@staticmethod
	def from_int(value):
		return Integer(rbigint.fromint(value))

	@staticmethod
	def from_decimal(value):
		return Integer(rbigint.fromdecimalstr(value))
	@staticmethod
	def from_string(value):
		assert isinstance(value, String)
		return Integer(rbigint.fromdecimalstr(value.value))

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

class String(Value):
	"""A sequence of Unicode codepoints.
	
	Not to be confused with Python 2's sequence of bytes!
	"""
	def __init__(self, value):
		"""Initialize from a Unicode string."""
		assert isinstance(value, unicode)
		
		Value.__init__(self, u'"' + value + u'"')
		self.value = value
	
	@staticmethod
	def from_bytes(bytes, encoding="utf-8"):
		"""Construct a string from an encoded sequence of bytes.
		
		Default encoding is utf-8. (TODO: should this always be explicit?)
		"""
		return String(bytes.decode(encoding))
	
	def bool(self):
		return self.value != u''
	
	def eq(self, other):
		"""Is this string equivalent to another?
		
		As a convenience, also supports equivalence to unicode.
		"""
		if isinstance(other, String):
			return self.value == other.value
		elif isinstance(other, unicode):
			return self.value == other
		else:
			return False
	
	def __unicode__(self):
		return self.value
