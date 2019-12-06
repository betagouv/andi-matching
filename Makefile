# TODO: Add unit tests

install:
	pipenv install --dev

tests: flake8 pylint-fail-under unittests

flake8:
	pipenv run flake8

pylint:
	find . -name "*.py" -not -path '*/\.*' -exec pipenv run pylint --rcfile=.pylintrc '{}' +

pylint-fail-under:
	find . -name "*.py" -not -path '*/\.*' -exec pipenv run pylint-fail-under --fail_under 9.5 --rcfile=.pylintrc '{}' +

serve-dev:
	export PYTHONPATH=${PYTHONPATH}:./ && pipenv run ./webservice/main.py --debug

serve:
	export PYTHONPATH=${PYTHONPATH}:./ && ./webservice/main.py

unittests:
	PYTHONPATH=${PYTHONPATH}:./:./matching:./webservice pipenv run pytest --cov=./webservice .

isort:
	pipenv run isort ./**/*.py
