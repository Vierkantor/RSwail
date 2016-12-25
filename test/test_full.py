#!/usr/bin/env python2

import pytest

from target import entry_point

def test_empty_file():
	"""The interpreter should accept an empty file."""
	entry_point(["swail", "example/triv.swa"])

def test_hello_file(capsys):
	"""The hello world program should output exactly this string:
		u"Hello, World!\n"
	"""
	entry_point(["swail", "example/hello.swa"])
	out, err = capsys.readouterr()
	assert out == u"Hello, World!\n"
