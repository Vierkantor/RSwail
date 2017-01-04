#!/usr/bin/env python2

import pytest

from rpython.rlib.rbigint import rbigint

from rswail.value import Boolean, Integer, String, Value

def test_integer_from_int():
	"""Making an integer from an int should be equivalent to going via rbigint."""
	assert Integer.from_int(37).eq(Integer(rbigint.fromint(37)))

def test_stringify_int():
	"""Make sure base values have their representation as name."""
	assert Integer(rbigint.fromint(37)).name == u"37"
	assert Integer(rbigint.fromint(0)).name == u"0"
	assert Integer(rbigint.fromint(-42)).name == u"-42"
	# and the same with the .get method
	assert Integer(rbigint.fromint(37)).get(u"name").eq(String(u"37"))

def test_stringify_bool():
	"""Make sure base values have their representation as name."""
	assert Boolean(True).name == u"True"
	assert Boolean(False).name == u"False"

def test_stringify_string():
	"""Make sure base values have their representation as name."""
	assert String(u"hello").name == u'"hello"'
	assert String(u"").name == u'""'
	# TODO: implement escaping and enable this:
	# assert String(u"\"").name == u'"\""'

def test_set_and_get():
	"""Set and get a value's attributes."""
	# set the attribute
	value = Value(u"value")
	attr = String(u"some string")
	value.set(u"some-attribute", attr)
	
	# get the attribute
	assert value.get(u"some-attribute").eq(attr)
	assert value.get(u"some-attribute").eq(String(u"some string"))
	
	# replace the attribute
	new_attr = String(u"different string")
	value.set(u"some-attribute", new_attr)
	assert not value.get(u"some-attribute").eq(attr)
	assert value.get(u"some-attribute").eq(new_attr)
