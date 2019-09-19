# TODO: Add unit tests

install:
	pipenv install --dev

tests: flake8 pylint

flake8:
	pipenv run flake8

pylint:
	find . -name "*.py" -not -path '*/\.*' -exec pipenv run pylint --rcfile=.pylintrc '{}' +

isort:
	pipenv run isort
