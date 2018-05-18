#!/bin/bash
source env/bin/activate; rm -rf daemon/migrations; yes yes | ./manage.py reset_db; ./manage.py makemigrations daemon; ./manage.py migrate --run-syncdb; ./manage.py loaddata users;