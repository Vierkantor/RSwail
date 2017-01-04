#!/usr/bin/env python2

from __future__ import unicode_literals

import pytest

from rpython.rlib.rbigint import rbigint

from rswail.value import Boolean, Integer, String, Unit, Value

def test_integer_from_int():
	"""Making an integer from an int should be equivalent to going via rbigint."""
	assert Integer.from_int(37).eq(Integer(rbigint.fromint(37)))
def test_integer_from_string():
	"""Making an integer from a string should be equivalent to going via int."""
	assert Integer.from_int(37).eq(Integer.from_decimal(u"37"))
	assert Integer.from_int(37).eq(Integer.from_string(String(u"37")))

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

def test_convert_to_bool():
	"""Convert Values, Integers, Booleans and Strings to booleans."""
	# a value is true by default
	assert Value(u"value").bool()
	# a unit is false
	assert not Unit().bool()
	# a boolean is itself
	assert Boolean(True).bool()
	assert not Boolean(False).bool()
	# an integer is true when nonzero
	assert Integer.from_int(1).bool()
	assert not Integer.from_int(0).bool()
	assert Integer.from_int(57).bool()
	assert Integer.from_int(-1).bool()
	# a string is true when not empty
	assert String(u"some words").bool()
	assert String(u" ").bool()
	assert String(u"\n").bool()
	assert not String(u"").bool()

def test_value_eq():
	"""Check the fallback eq method on Value check references are identical.
	
	This should happen even when the values have exactly the same attributes.
	"""
	value1 = Value(u"value")
	value2 = Value(u"value")
	
	assert value1.eq(value1)
	assert not value1.eq(value2)
	assert not value2.eq(value1)
	assert value2.eq(value2)

def test_overload_raises():
	"""Make sure the overloaded operators raise an exception.
	
	Those operators work differently in Python and RPython so we can't test them.
	"""
	value = Value(u"value")
	
	with pytest.raises(Exception):
		assert value == value
	with pytest.raises(Exception):
		assert not (value != value)

def test_unit_eq():
	"""Any Unit should equal another Unit, but nothing else."""
	unit1 = Unit()
	unit2 = Unit()
	value = Value(u"value")
	
	assert unit1.eq(unit1)
	assert unit1.eq(unit2)
	assert unit2.eq(unit1)
	assert unit2.eq(unit2)
	assert not value.eq(unit1)
	assert not value.eq(unit2)
	assert not unit1.eq(value)
	assert not unit2.eq(value)

def test_bool_eq():
	"""Booleans should be equivalent when they have the same python value.
	
	They should also be equivalent to a python bool.
	(But not to everything that has a __bool__ or .bool method!)
	"""
	assert Boolean(True).eq(Boolean(True))
	assert not Boolean(True).eq(Boolean(False))
	assert not Boolean(False).eq(Boolean(True))
	assert Boolean(False).eq(Boolean(False))
	
	assert Boolean(True).eq(True)
	assert not Boolean(True).eq(1)
	assert not Boolean(True).eq(Integer.from_int(1))
	assert not Boolean(True).eq(u"foo")
	assert not Boolean(True).eq(String(u"foo"))
	assert Boolean(False).eq(False)
	assert not Boolean(False).eq(0)
	assert not Boolean(False).eq(Integer.from_int(0))
	assert not Boolean(False).eq(u"")
	assert not Boolean(False).eq(String(u""))
	
	# also make sure we don't just check the attributes are the same
	value = Value(u"value")
	value.value = True
	assert not Boolean(True).eq(value)

def test_int_eq():
	"""Integers should be equivalent when they have the same python value.
	
	They should also be equivalent to a python int or a rbigint.
	"""
	assert Integer.from_int(0).eq(Integer.from_int(0))
	assert not Integer.from_int(0).eq(Integer.from_int(1))
	assert Integer.from_int(1).eq(Integer.from_int(1))
	assert not Integer.from_int(1).eq(Integer.from_int(-1))
	# use a big value since in python 1 is 1 but 32767 is not 32767
	assert Integer.from_int(32767).eq(Integer.from_int(32767))
	assert not Integer.from_int(32767).eq(Integer.from_int(32768))
	
	assert Integer.from_int(0).eq(0)
	assert not Integer.from_int(0).eq(1)
	assert Integer.from_int(1).eq(1)
	assert not Integer.from_int(1).eq(-1)
	assert Integer.from_int(32767).eq(32767)
	assert not Integer.from_int(32767).eq(32768)
	
	assert Integer.from_int(0).eq(rbigint.fromint(0))
	assert not Integer.from_int(0).eq(rbigint.fromint(1))
	assert Integer.from_int(1).eq(rbigint.fromint(1))
	assert not Integer.from_int(1).eq(rbigint.fromint(-1))
	assert Integer.from_int(32767).eq(rbigint.fromint(32767))
	assert not Integer.from_int(32767).eq(rbigint.fromint(32768))
	
	# also make sure we don't just check the attributes are the same
	value = Value(u"value")
	value.value = rbigint.fromint(1)
	assert not Integer.from_int(1).eq(value)

def test_string_eq():
	"""Integers should be equivalent when they have the same python value.
	
	They should also be equivalent to a python (unicode) string.
	"""
	assert String(u"").eq(String(u""))
	assert not String(u"").eq(String(u"foo"))
	assert not String(u"foo").eq(String(u""))
	assert String(u"foo").eq(String(u"foo"))
	# a en-dash not in ASCII shouldn't be truncated or become UTF-8 bytes
	assert String(u"A\u2013Eskwadraat").eq(String(u"A\u2013Eskwadraat"))
	assert not String(u"A\u2013Eskwadraat").eq(String(u"A"))
	assert not String(u"A\u2013Eskwadraat").eq(String(u"A\xe2\x80\x93Eskwadraat"))
	# an emoji not in the BMP shouldn't be truncated or become any UTF-16 variant
	assert String(u"ok \U0001f44c").eq(String(u"ok \U0001f44c"))
	assert not String(u"ok \U0001f44c").eq(String(u"ok "))
	assert not String(u"ok \U0001f44c").eq(String(u"\ufffeok \u3dd8\u4cdc")) # with BOM
	assert not String(u"ok \U0001f44c").eq(String(u"ok \u3dd8\u4cdc")) # big endian
	assert not String(u"ok \U0001f44c").eq(String(u"ok \ud83d\ucd4c")) # little endian
	
	# automatically convert python strings
	assert String(u"").eq(u"")
	assert String(u"foo").eq(u"foo")
	assert String(u"A\u2013Eskwadraat").eq(u"A\u2013Eskwadraat")
	assert String(u"ok \U0001f44c").eq(u"ok \U0001f44c")
	
	# but don't do bytes!
	assert not String(u"").eq(b"")
	assert not String(u"foo").eq(b"foo")
	assert not String(u"A\u2013Eskwadraat").eq(b"A\u2013Eskwadraat")
	assert not String(u"ok \U0001f44c").eq(b"\U0001f44c")
	
	# also make sure we don't just check the attributes are the same
	value = Value(u"value")
	value.value = u"foo"
	assert not String(u"foo").eq(value)

def test_string_from_bytes():
	"""Decoding a String from bytes is equivalent to the corresponding unicode."""
	assert String.from_bytes(b"").eq(u"")
	assert String.from_bytes(b"foo").eq(u"foo")
	assert String.from_bytes(b"A\xe2\x80\x93Eskwadraat").eq(u"A\u2013Eskwadraat")
	assert String.from_bytes(b"ok \xf0\x9f\x91\x8c").eq(u"ok \U0001f44c")
	# non-utf-8 encodings
	assert String.from_bytes(b"Espa\xf1a", encoding='latin-1').eq(u"Espa\xf1a")
	assert String.from_bytes(b"\x83n\x83\x8d\x81[\x83\x8f\x81[\x83\x8b\x83h",
			encoding='shift_jis').eq(u"\u30cf\u30ed\u30fc\u30ef\u30fc\u30eb\u30c9")
