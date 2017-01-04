import pytest

from rswail.struct import Struct, construct
from rswail.value import String

def test_get_struct_member():
	"""Define a struct and get one of its members."""
	struct = Struct(u"maybe", {u"nothing": [], u"just": [u"value"]})

	assert struct.members[u"nothing"].eq(struct.get(u"nothing"))
	assert struct.members[u"just"].eq(struct.get(u"just"))
	assert struct.get(u"name").eq(u"maybe")

def test_set_struct_member():
	"""Define a struct and set one of its members."""
	maybe = Struct(u"maybe", {u"nothing": [], u"just": [u"value"]})
	perhaps = Struct(u"perhaps", {u"nothing": [], u"just": [u"value"]})

	perhaps.set(u"nothing", maybe.get(u"nothing"))
	perhaps.set(u"just", maybe.get(u"just"))
	perhaps.set(u"some-random-key", String(u"some random value"))

	assert perhaps.members[u"nothing"].eq(maybe.get(u"nothing"))
	assert perhaps.members[u"just"].eq(maybe.get(u"just"))
	assert u"some-random-key" not in perhaps.members

def test_struct_equivalence():
	"""Check when instances of a struct say they're equivalent."""
	struct = Struct(u"maybe", {u"nothing": [], u"just": [u"value"]})
	instance_nothing = construct(struct, u"nothing")
	some_value = String(u"Hello!")
	instance_just = construct(struct, u"just", some_value)
	
	# equivalence should be reflexive
	assert instance_nothing.eq(instance_nothing)
	# and agree on identical values
	assert instance_nothing.eq(construct(struct, u"nothing"))
	assert instance_just.eq(construct(struct, u"just", some_value))
	assert instance_just.eq(construct(struct, u"just", String(u"Hello!")))
	# but disagree on different values
	assert not instance_nothing.eq(instance_just)
	assert not instance_just.eq(some_value)
	assert not instance_just.eq(construct(struct, u"just", String(u"Goodbye!")))
	# maybe this should just raise an error, but they're definitely different
	assert not instance_just.eq(construct(struct, u"just"))
