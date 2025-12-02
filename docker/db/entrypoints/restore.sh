#!/bin/bash
set -e

echo "Restoring database from custom-format dump..."
pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" "$BASEOSM_DUMP"
echo "Database restore complete."
