#!/bin/sh

echo "🛠️ Waiting for DB to be ready..."
sleep 5

echo "⚙️ Applying migrations..."
python manage.py migrate --noinput

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo "🚀 Starting server..."
exec "$@"
