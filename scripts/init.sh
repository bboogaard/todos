#!/bin/bash

python manage.py migrate --settings=app.settings-docker
python manage.py createcachetable --settings=app.settings-docker
python manage.py loaddata wallpapers.json --settings=app.settings-docker
python manage.py loaddata widgets.json --settings=app.settings-docker
python manage.py loaddata dates.json --settings=app.settings-docker
python manage.py collectstatic --no-input --settings=app.settings-docker
python manage.py collectmedia --noinput --settings=app.settings-docker
python manage.py rebuild_index --noinput --settings=app.settings-docker