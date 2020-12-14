PYTHON ?= /usr/bin/env python

install :
	$(PYTHON) setup.py install

develop :
	$(PYTHON) setup.py develop
