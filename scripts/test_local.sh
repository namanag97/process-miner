#!/bin/bash
set -e

# A script to run backend tests locally

echo "Starting Backend Tests..."

if command -v pytest &> /dev/null; then
    echo "Running pytest directly..."
    cd backend
    pytest -v
else
    echo "pytest not found separately. Attempting to use docker..."
    # Build a temporary test container just to run tests
    docker build -t process-miner-test -f Dockerfile.backend .
    echo "Running tests inside container..."
    # Check if we need to install tests dev deps if they aren't in requirements.txt (they are)
    # We override the CMD to run pytest
    docker run --rm process-miner-test pytest -v
fi

echo "Tests Completed!"
