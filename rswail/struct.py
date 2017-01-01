from rswail.value import Value

class Struct(Value):
	def __init__(self, name, member_dict):
		# initialize members first so we can't overwrite it
		self.members = {}
		Value.__init__(self, name)
		for key, value in member_dict.items():
			member = StructMember(self, key, value)
			self.members[key] = member
		self.set(u"members", self.members)
	def get(self, key):
		assert isinstance(key, unicode)
		if key in self.members:
			return self.members[key]
		return Value.get(self, key)
	def set(self, key, value):
		assert isinstance(key, unicode)
		if key in self.members:
			self.members[key] = value
		else:
			Value.set(self, key, value)

class StructMember(Value):
	def __init__(self, parent, name, fields):
		Value.__init__(self, name)
		self.parent = parent
		self.fields = fields
		self.set(u"parent", parent)
		self.set(u"name", name)
		self.set(u"fields", fields)

class StructInstance(Value):
	def __init__(self, name, member, values):
		Value.__init__(self, name)
		self.member = member
		self.values = values
		self.set(u"member", member)
		self.set(u"values", values)
	def __repr__(self):
		return repr(self.member) + repr(self.values)

def construct(struct, member_name, *args):
	"""Make a new StructInstance.
	
	The member_name is the (canonical) name of the struct's instance,
	attributes that resolve to a member are ignored.
	"""
	assert isinstance(struct, Struct)
	assert isinstance(member_name, unicode)
	return StructInstance(member_name, struct.members[member_name], args)
