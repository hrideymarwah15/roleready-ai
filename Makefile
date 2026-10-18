.PHONY: help install dev test lint format clean run docker-build docker-up docker-down

help:
	@echo "🎓 AI-Adaptive Onboarding Engine"
	@echo ""
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make dev          - Run dev server with auto-reload"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linting (flake8)"
	@echo "  make format       - Format code (black)"
	@echo "  make clean        - Remove cache and build files"
	@echo "  make run          - Run production server"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-up    - Run with Docker Compose"
	@echo "  make docker-down  - Stop Docker Compose"

install:
	pip install -r requirements.txt

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest --cov=app tests/

lint:
	flake8 app tests --max-line-length=100

format:
	black app tests

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov dist build *.egg-info

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

docker-build:
	docker build -t onboarding-engine .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docs:
	@echo "📚 API Documentation available at: http://localhost:8000/docs"
	@echo "   Alternative docs at: http://localhost:8000/redoc"

.DEFAULT_GOAL := help
