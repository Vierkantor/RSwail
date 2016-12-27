#!/usr/bin/env python2

import pytest

from rpython.rlib.rbigint import rbigint

from rswail.value import Boolean, Integer

def test_stringify_int():
	assert Integer(rbigint.fromint(37)).name == u"37"
	assert Integer(rbigint.fromint(0)).name == u"0"
	assert Integer(rbigint.fromint(-42)).name == u"-42"

def test_stringity_bool():
	assert Boolean(True).name == u"True"
	assert Boolean(False).name == u"False"
