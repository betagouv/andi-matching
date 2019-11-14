# TODO: Add unit tests

install:
	pipenv install --dev

tests: flake8 pylint

flake8:
	pipenv run flake8

pylint:
	find . -name "*.py" -not -path '*/\.*' -exec pipenv run pylint --rcfile=.pylintrc '{}' +

serve-dev:
	export PYTHONPATH=$PYTHONPATH:./ && pipenv run ./webservice/main.py

serve:
	export PYTHONPATH=$PYTHONPATH:./ && ./webservice/main.py

isort:
	pipenv run isort
