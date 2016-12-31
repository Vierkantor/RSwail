#!/usr/bin/env python2

import pytest

from target import entry_point, target

def test_empty_file():
	"""The interpreter should accept an empty file."""
	exit_code = entry_point(["swail", "example/triv.swa"])
	assert exit_code == 0

def test_hello_file(capsys):
	"""The hello world program should output exactly this string:
		u"Hello, World!\n"
	"""
	exit_code = entry_point(["swail", "example/hello.swa"])
	assert exit_code == 0
	out, err = capsys.readouterr()
	assert out == u"Hello, World!\n"

def test_builtin_tests():
	"""The builtin tests should run successfully."""
	assert entry_point(["swail", "tests.swa"]) == 0

def test_missing_file():
	"""Report an error but gracefully exit when the file to run isn't specified."""
	assert entry_point(["swail"]) != 0

def test_target_exists():
	"""We can get a compilation target."""
	assert target() == (entry_point, None)
