from rswail.value import Value

class Struct(Value):
	def __init__(self, name, member_dict):
		Value.__init__(self, name)
		members = []
		for key, value in member_dict.items():
			members.append(StructMember(self, key, value))
		self.members = members
		self.set(u"members", members)
	def get(self, key):
		assert isinstance(unicode, key)
		if key in self.members:
			return self.members[key]
		return Value.get(self, key)
	def set(self, key, value):
		assert isinstance(unicode, key)
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

statement = Struct(u"statement", {
	u"declaration": [u"header", u"name", u"args", u"body"],
	u"expression": [u"expr"],
})

expression = Struct(u"expression", {
	u"name_access": [u"name"],
	u"apply": [u"func", u"args"],
	u"base_value": [u"value"],
})
