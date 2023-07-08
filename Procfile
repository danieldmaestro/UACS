web: python manage.py makemigrations && python manage.py migrate && python manage.py collectstatic --no-input && gunicorn EMS.wsgi && python manage.py spectacular --file schema.yml
