install-deps: deps
	pip-sync requirements.txt

deps:
	pip-compile requirements.in

lint:
	flake8 src
