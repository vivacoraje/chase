VENV = venv

venv: $(VENV)/.installed
$(VENV)/.installed: Makefile
	python3 -mvenv $(VENV)
	$(VENV)/bin/python3 -mensurepip
	$(VENV)/bin/pip install -U pip
	$(VENV)/bin/pip install -U setuptools wheel
	$(VENV)/bin/pip install -r requirements.txt
	touch $(VENV)/.installed

run:
	gunicorn -b 0.0.0.0:5000 wsgi:application --access-logfile -

worker:
	python manage.py celery worker

beat:
	python manage.py celery beat

test:
	py.test tests

.PHONY:
	test lint run worker 

clean:
	rm -rf $(VENV) .coverage
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '.pytest_cache' -exec rm -rf {} +
	find . -name 'venv' -exec rm -rf {} +

docker:
	COMPOSE_FILE=docker-compose.yml docker-compose up --build
