##############################################################################
#
# Copyright (C) Zenoss, Inc. 2015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

default: help

help:
	@echo "Please use 'make <target>' where <target> is one of.."
	@echo "  test    Runs all tests in tests/ directory."

test:
	python -m unittest discover -s tests
