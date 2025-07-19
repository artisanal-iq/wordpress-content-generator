#!/bin/bash

# Install test dependencies if needed
pip install -r test-requirements.txt

# Run pytest with coverage
pytest tests/unit/ tests/integration/ --cov=./ --cov-report=term --cov-report=xml:coverage.xml

# Run linting checks
echo "Running flake8..."
flake8 .

echo "Running black (check only)..."
black --check .

echo "Running isort (check only)..."
isort --check-only .
