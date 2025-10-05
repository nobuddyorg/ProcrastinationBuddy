#!/usr/bin/env bash
set -euo pipefail

EXISTS=$(psql -U "$POSTGRES_USER" -d postgres -At -c "select 1 from pg_database where datname = 'tasks'")
if [[ "$EXISTS" != "1" ]]; then
  psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d postgres -c "create database tasks owner \"$POSTGRES_USER\";"
fi
