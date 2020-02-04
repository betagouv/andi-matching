# TODO: Add unit tests

install:
	pipenv install --dev

tests: flake8 pylint-fail-under unittests behave

flake8:
	pipenv run flake8

pylint:
	find . -name "*.py" -not -path '*/\.*' -exec pipenv run pylint --rcfile=.pylintrc '{}' +

pylint-fail-under:
	find . -name "*.py" -not -path '*/\.*' -exec pipenv run pylint-fail-under --fail_under 9.5 --rcfile=.pylintrc '{}' +

behave:
	export NO_ASYNCPG=true && export PYTHONPATH=${PYTHONPATH}:./:./matching:./webservice && pipenv run behave tests/behave

behave-debug:
	pipenv run behave tests/behave --logging-level=DEBUG --no-logcapture

serve-dev:
	export PYTHONPATH=${PYTHONPATH}:./ && pipenv run ./webservice/main.py --debug

serve:
	export PYTHONPATH=${PYTHONPATH}:./ && ./webservice/main.py

unittests:
	PYTHONPATH=${PYTHONPATH}:./:./matching:./webservice pipenv run pytest --cov=./webservice .

isort:
	pipenv run isort ./**/*.py
