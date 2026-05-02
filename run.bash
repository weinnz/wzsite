#source .venv/bin/activate
python3 manage.py collectstatic
python3 manage.py clear_cache --all
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver
