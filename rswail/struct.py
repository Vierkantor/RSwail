from rswail.value import Value

class Struct(Value):
	def __init__(self, name, member_dict):
		# initialize members first so we can't overwrite it
		self.members = {}
		Value.__init__(self, name)
		for key, value in member_dict.items():
			member = StructMember(self, key, value)
			self.members[key] = member
	def get(self, key):
		assert isinstance(key, unicode)
		if key in self.members:
			return self.members[key]
		return Value.get(self, key)
	def set(self, key, value):
		assert isinstance(key, unicode)
		if key in self.members:
			assert isinstance(value, StructMember)
			self.members[key] = value
		else:
			Value.set(self, key, value)

class StructMember(Value):
	def __init__(self, parent, name, fields):
		Value.__init__(self, name)
		self.parent = parent
		self.fields = fields

class StructInstance(Value):
	def __init__(self, name, member, values):
		assert isinstance(member, StructMember)
		Value.__init__(self, name)
		self.member = member
		self.values = values
	def eq(self, other):
		"""Is this instance equivalent to another?
		
		Equivalent instances have the (exact) same member and each value is equivalent.
		"""
		if self is other:
			return True
		if not isinstance(other, StructInstance):
			return False
		if self.member is not other.member:
			return False
		if len(self.values) != len(other.values):
			return False
		for self_val, other_val in zip(self.values, other.values):
			assert isinstance(self_val, Value)
			assert isinstance(other_val, Value)
			if not self_val.eq(other_val):
				return False
		return True
	def __repr__(self):
		return repr(self.member) + repr(self.values)

def construct(struct, member_name, *args):
	"""Make a new StructInstance.
	
	The member_name is the (canonical) name of the struct's instance,
	attributes that resolve to a member are ignored.
	"""
	assert isinstance(struct, Struct)
	assert isinstance(member_name, unicode)
	for value in args:
		assert isinstance(value, Value)
	return StructInstance(member_name, struct.members[member_name], args)
