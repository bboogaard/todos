#!/bin/bash

source /home/bboogaard/vens/py-todos/bin/activate && source /home/bboogaard/vens/py-todos/bin/postactivate && /home/bboogaard/vens/py-todos/bin/python /home/bboogaard/apps/py-todos/manage.py migrate --settings=app.settings-strato
source /home/bboogaard/vens/py-todos/bin/activate && source /home/bboogaard/vens/py-todos/bin/postactivate && /home/bboogaard/vens/py-todos/bin/python /home/bboogaard/apps/py-todos/manage.py createcachetable --settings=app.settings-strato
source /home/bboogaard/vens/py-todos/bin/activate && source /home/bboogaard/vens/py-todos/bin/postactivate && /home/bboogaard/vens/py-todos/bin/python /home/bboogaard/apps/py-todos/manage.py loaddata wallpapers.json --settings=app.settings-strato
source /home/bboogaard/vens/py-todos/bin/activate && source /home/bboogaard/vens/py-todos/bin/postactivate && /home/bboogaard/vens/py-todos/bin/python /home/bboogaard/apps/py-todos/manage.py loaddata widgets.json --settings=app.settings-strato
source /home/bboogaard/vens/py-todos/bin/activate && source /home/bboogaard/vens/py-todos/bin/postactivate && /home/bboogaard/vens/py-todos/bin/python /home/bboogaard/apps/py-todos/manage.py collectstatic --no-input --settings=app.settings-strato
source /home/bboogaard/vens/py-todos/bin/activate && source /home/bboogaard/vens/py-todos/bin/postactivate && /home/bboogaard/vens/py-todos/bin/python /home/bboogaard/apps/py-todos/manage.py collectmedia --noinput --settings=app.settings-strato
source /home/bboogaard/vens/py-todos/bin/activate && source /home/bboogaard/vens/py-todos/bin/postactivate && /home/bboogaard/vens/py-todos/bin/python /home/bboogaard/apps/py-todos/manage.py rebuild_index --noinput --settings=app.settings-strato
