SHELL := /bin/sh

.PHONY: configure
configure:
	python3 -m venv .venv

.PHONY: requirements
requirements:
	source .venv/bin/activate
	pip install -r requirements.txt

.PHONY: package
package:
	python3 -m build

.PHONY: publish
publish:
	python3 -m twine upload --repository testpypi dist/*

.PHONY: install
install:
	python3 -m pip install --index-url https://test.pypi.org/simple --no-deps zfr-nathonfowlie

.PHONY: dev-install
dev-install:
	pip install --editable .
