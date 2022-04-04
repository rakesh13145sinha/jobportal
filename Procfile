release:python manage.py makemigrations --no-input
release:python manage.py migrate --no-input 
release: nohup python manage.py runserver 0.0.0.0:8000
web:gunicorn jobportal.wsgi