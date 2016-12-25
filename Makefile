PYTHON2 ?= /usr/bin/env python2
PYTEST2 ?= ${PYTHON2} -m pytest
PYPY2 ?= /usr/bin/env pypy

all: tests swail

.PHONY: tests
tests:
	${PYTEST2}

swail: target-c
	mv target-c swail

.PHONY: target-c
target-c: target.py
	${PYPY2} pypy/rpython/bin/rpython --opt=jit target.py
