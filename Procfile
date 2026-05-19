web: python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn bakery_erp.wsgi --workers 2 --timeout 120 --log-file -
