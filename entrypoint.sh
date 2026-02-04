#!/bin/bash
set -e

echo "Warming up products cache..."
python manage.py shell -c "
from service.tasks import refresh_products_cache
try:
    result = refresh_products_cache()
    print(result)
except Exception as e:
    print(f'Cache warmup failed: {e}')
"

echo "Starting Gunicorn..."
exec "$@"
