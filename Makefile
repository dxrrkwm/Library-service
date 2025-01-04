PYTHON = python
POETRY = poetry
PROJECT_NAME = Library-service
CONTAINER_NAME = ${PROJECT_NAME}_container
DOCKER-COMPOSE = docker-compose -f compose.yaml

.PHONY: help
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  deps      Install dependencies with Poetry"
	@echo "  up        Start the application"
	@echo "  down      Stop the application"
	@echo "  migrate   Apply database migrations inside the container"
	@echo "  createsu  Create superuser inside the container"
	@echo "  test      Run tests"
	@echo "  lint      Run Ruff"
	@echo "  clean     Remove cache files"
	@echo "  loaddata  Load initial data"
	@echo "  up build   Start the application with build"
	@echo "  build     Build the application"

.PHONY: deps
deps:
	${POETRY} install

.PHONY: build
build:
	${DOCKER-COMPOSE} build

.PHONY: up build
build:
	${DOCKER-COMPOSE} up --build

.PHONY: up
up:
	${DOCKER-COMPOSE} up

.PHONY: down
down:
	${DOCKER-COMPOSE} down

.PHONY: migrate
migrate:
	${DOCKER-COMPOSE} exec app python manage.py migrate

.PHONY: createsu
createsu:
	${DOCKER-COMPOSE} exec app python manage.py createsuperuser

.PHONY: test
test:
	${DOCKER-COMPOSE} exec app python manage.py test

.PHONY: lint
lint:
	${POETRY} run ruff check --fix

.PHONY: loaddata
loaddata:
	${DOCKER-COMPOSE} exec app python manage.py loaddata sample_books_service.json

.PHONY: clean
clean:
	find . -name "__pycache__" -exec rm -rf {} +
