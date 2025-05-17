#!/bin/bash

case "$1" in
  start)
    if ! docker info > /dev/null 2>&1
    then
        echo "docker is not installed/running"
        exit 1
    fi

    echo "Starting docker containers..."
    docker compose pull
    docker compose up --build --force-recreate --detach

    echo "Waiting for Ollama to be ready..."
    until curl -s http://localhost:11434 | grep -q "Ollama is running"; do
      echo -n "."
      sleep 1
    done

    echo "Downloading initial model (llama3:8b)..."
    curl -s -X POST http://localhost:11434/api/pull -d '{"name": "llama3:8b"}'

    echo -e "\033[0;32m##################################\033[0m"
    echo -e "\033[0;32mAccess UI at http://localhost:8501\033[0m"
    echo -e "\033[0;32m##################################\033[0m"
    ;;

  stop)
    echo "Stopping docker containers..."
    docker compose down
    ;;

  test)
    echo "Running tests..."
    echo "Running E2E-Tests..."
    pushd e2e-tests
    ./npmw ci
    ./npmw run install
    ./npmw run test
    popd
    ;;

  *)
    echo "Usage: $0 <command>"
    echo ""
    echo "Commands:"
    echo "  start   Start the Docker services and wait for Ollama to be ready"
    echo "  stop    Stop all running Docker services"
    echo "  test    Run all (E2E) tests"
    exit 1
    ;;
esac
