#!/usr/bin/env python2
import sys
sys.path.append("pypy")

def pytest_configure(config):
	"""Called when pytest is starting up."""
	# Make sure python's operator overloading is disabled on Values
	import rswail.value
	rswail.value._strict_operators = True

def pytest_unconfigure(config):
	"""Called when pytest is shutting down."""
	import rswail.value
	rswail.value._strict_operators = False
