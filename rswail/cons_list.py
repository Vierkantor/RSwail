from rswail.struct import Struct, construct

"""Implement a list of elements as an algebraic data structure.

This has a lot worse performance than array lists so we probably want to make
some form of optimization that allows us to use any kind of list.

Currently, we use cons-lists during parsing since it's easier to program.
"""
cons_list = Struct(u"cons-list", {
	u"empty": [],
	u"cons": [u"head", u"tail"],
})

def empty():
	"""Make a new empty list."""
	return construct(cons_list, u"empty")

def cons(head, tail):
	"""Add an element to the beginning of the list.
	
	To add an element to the end, use append.
	"""
	assert tail.member.parent == cons_list
	return construct(cons_list, u"cons", head, tail)

def singleton(element):
	"""Make a list with one element."""
	return cons(element, empty())

def append(list, element):
	"""Add an element to the end of the list.
	
	To add an element to the beginning, use cons.
	"""
	if list.member == cons_list.members[u"empty"]:
		return cons(element, empty())
	else:
		assert list.member == cons_list.members[u"cons"]
		head, tail = list.values
		return cons(head, append(tail, element))

def extend(list1, list2):
	"""Make a list from the elements of list1 succeeded by the elements of list2."""
	if list1.member == cons_list.members[u"empty"]:
		return list2
	else:
		assert list1.member == cons_list.members[u"cons"]
		head, tail = list1.values
		return cons(head, extend(tail, list2))

def from_list(list):
	"""Convert a Python list to a cons-list."""
	result = empty()
	for element in list[::-1]:
		result = cons(element, result)
	return result

def to_list(list):
	"""Convert a cons-list to a Python list."""
	result = []
	while list.member != cons_list.members[u"empty"]:
		assert list.member == cons_list.members[u"cons"]
		head, list = list.values
		result.append(head)
	return result

def length(list):
	"""Count the number of elements in the list."""
	if list.member == cons_list.members[u"empty"]:
		return 0
	else:
		assert list.member == cons_list.members[u"cons"]
		head, tail = list.values
		return 1 + length(tail)

def index(list, index):
	"""Get the element at a specified index.
	
	Replacement for the [] operator.
	
	If index < 0 or index >= length(list), raises an IndexError.
	
	list must be a cons-list instance,
	index must be an int.
	"""
	if index < 0:
		raise IndexError("negative index in cons-list")
	if list.member == cons_list.members[u"empty"]:
		raise IndexError("too large index in cons-list")
	assert list.member == cons_list.members[u"cons"]
	head, tail = list.values
	if index == 0:
		return head
	else:
		return index(tail, index-1)

