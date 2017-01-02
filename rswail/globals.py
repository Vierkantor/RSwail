from rswail.function import NativeFunction

def hello(args):
	assert len(args) == 0
	print(u"Hello, World!")

def make_globals():
	return {
			u"hello": NativeFunction(u"hello", hello),
	}
