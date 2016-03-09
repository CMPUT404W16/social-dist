.PHONY: all
all: sphinx

# No -W for doctests because that disallows tests with empty output.
SPHINX_DOCTEST_OPTS=-n -d build/doctress .
SPHINXOPTS=-n -d build/doctrees .

.PHONY: sphinx
sphinx:
	sphinx-build -b html $(SPHINXOPTS) build/html

.PHONY: coverage
coverage:
	sphinx-build -b coverage ${SPHINXOPTS} build/coverage
	cat build/coverage/python.txt

.PHONY: doctest
doctest:
	sphinx-build -b doctest $(SPHINX_DOCTEST_OPTS) build/doctest

clean:
	rm -rf build
