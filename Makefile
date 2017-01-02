PYTHON2 ?= /usr/bin/env python2
PYTEST2 ?= ${PYTHON2} -m pytest
PYPY2 ?= /usr/bin/env pypy

.PHONY: all
all: swail
.PHONY: test
test: swail
	./swail tests.swa

# Tests that should be run before the full compilation that includes JIT.
.PHONY: test-interpreted
test-interpreted:
	${PYTEST2} --cov=.
	${PYTHON2} target.py tests.swa
.PHONY: test-nojit
test-nojit: swail-nojit
	./swail-nojit tests.swa

# Various rules to make the compiler.
# Depend on tests so that we don't waste time compiling something that doesn't
# work anyway.
.PHONY: swail
swail: test-nojit
	${PYPY2} pypy/rpython/bin/rpython --opt=jit target.py
	mv target-c swail
.PHONY: swail-nojit
swail-nojit: test-interpreted
	${PYPY2} pypy/rpython/bin/rpython target.py
	mv target-c swail-nojit

# Targets for making documentation.
.PHONY: docs
docs: docs-html
.PHONY: docs-html
docs-html:
	$(MAKE) -C docs html
