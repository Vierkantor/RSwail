import pytest

from rswail.cons_list import append, cons, empty, extend, from_list, index, length, singleton, to_list
from rswail.value import Integer

def test_empty_lists_equivalent():
	"""Two empty lists should be equivalent."""
	assert empty().eq(empty())

def test_singleton():
	"""Make a singleton list and test length and indexing."""
	list = singleton(Integer.from_int(5))
	assert length(list) == 1
	assert index(list, 0).eq(5)

def test_from_to_list():
	"""Convert cons-lists from and to lists."""
	# empty list
	assert empty().eq(from_list([]))
	assert to_list(empty()) == []

	# singleton
	cons_list = singleton(Integer.from_int(5))
	list = to_list(cons_list)
	assert len(list) == 1
	assert list[0].eq(5)
	assert cons_list.eq(from_list([Integer.from_int(5)]))

	# 3 elements
	cons_list = cons(Integer.from_int(1),
			cons(Integer.from_int(2),
			cons(Integer.from_int(3),
			empty())))
	list = to_list(cons_list)
	assert len(list) == 3
	assert list[0].eq(1)
	assert list[1].eq(2)
	assert list[2].eq(3)
	cons_list2 = from_list([Integer.from_int(1), Integer.from_int(2), Integer.from_int(3)])
	assert cons_list.eq(cons_list2)

def test_nonempty_lists_equivalent():
	"""Lists with the same contents should be equivalent.
	
	We test a variety of ways to make these lists.
	"""
	list1 = from_list(map(Integer.from_int, range(1, 5)))
	list2 = cons(Integer.from_int(1),
			cons(Integer.from_int(2),
			cons(Integer.from_int(3),
			cons(Integer.from_int(4),
			empty()))))
	list3 = empty()
	for i in range(1, 5):
		list3 = append(list3, Integer.from_int(i))
	list4 = extend(
			cons(Integer.from_int(1), cons(Integer.from_int(2), empty())),
			cons(Integer.from_int(3), cons(Integer.from_int(4), empty())),
	)
	assert list1.eq(list2)
	assert list1.eq(list3)
	assert list1.eq(list4)

def test_index_errors():
	"""Indexing with bad indices should give errors."""
	with pytest.raises(IndexError):
		index(empty(), 0)
	with pytest.raises(IndexError):
		index(cons(Integer.from_int(1), cons(Integer.from_int(2), empty())), 10)
	with pytest.raises(IndexError):
		index(cons(Integer.from_int(1), cons(Integer.from_int(2), empty())), 2)
	with pytest.raises(IndexError):
		index(cons(Integer.from_int(1), cons(Integer.from_int(2), empty())), -1)
