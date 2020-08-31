# TODO: Add unit tests

install:
	pip install -e .[dev]

tests: flake8 pylint-fail-under unittests

flake8:
	flake8

pylint:
	find . -name "*.py" -not -path '*/\.*' -exec pylint --rcfile=.pylintrc '{}' +

pylint-fail-under:
	find . -name "*.py" -not -path '*/\.*' -exec pylint-fail-under --fail_under 9.5 --rcfile=.pylintrc '{}' +

serve-dev:
	andi-api --debug

serve:
	andi-api

unittests:
	pytest

isort:
	isort ./**/*.py
