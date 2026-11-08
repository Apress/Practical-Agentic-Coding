#!/bin/sh
# LinkForge local launcher: start Postgres + Redis, wait until both are
# ready, then run the API. Teardown when done: docker compose down
set -eu
cd "$(dirname "$0")"

# docker-compose v1 fallback for older installs
if command -v docker-compose >/dev/null 2>&1; then DC="docker-compose"; else DC="docker compose"; fi

[ -f .env ] || cp .env.example .env

echo "Starting PostgreSQL and Redis..."
$DC up -d db redis

echo "Waiting for services to become ready..."
tries=0
until $DC exec -T db pg_isready -U postgres >/dev/null 2>&1 \
   && [ "$($DC exec -T redis redis-cli ping 2>/dev/null)" = "PONG" ]; do
    tries=$((tries + 1))
    if [ "$tries" -ge 30 ]; then
        echo "Services not ready after 60s; check '$DC logs db redis'" >&2
        exit 1
    fi
    sleep 2
done

echo "Services ready. Starting LinkForge on http://localhost:8000 ..."
# To run the test suite instead: pytest --cov=src
exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload --env-file .env
