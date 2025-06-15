#!/bin/bash
# Migration: Ensure password_hash column is large enough
set -e

# Wait until the DB is reachable
until mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e ";"; do
  echo "Waiting for database..."
  sleep 2
done

# Run migration (idempotent)
mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "ALTER TABLE users MODIFY password_hash VARCHAR(255);"

# Start the Flask app
exec python app.py
