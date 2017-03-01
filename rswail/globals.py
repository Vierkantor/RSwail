from rswail.function import CodeFunction, NativeFunction

def hello(args):
	assert len(args) == 0
	print(u"Hello, World!")

def def_(args):
	"""Create a new function."""
	# FIXME!

def make_globals():
	"""Make a list of global variables used in a block."""
	global_map = {
			u"hello": NativeFunction(u"hello", hello),
			u"def": NativeFunction(u"def", def_),
			u"rpython_is_weird": CodeFunction(u"rpython_is_weird", -1),
	}
	return global_map
