#!/usr/bin/env bash
set -o errexit

python -m pip install -r requirements.txt
python manage.py collectstatic --clear --noinput
python manage.py migrate --database=default --noinput
python manage.py migrate --database=auth_db --noinput
python manage.py migrate --database=orders_db --noinput
python manage.py check