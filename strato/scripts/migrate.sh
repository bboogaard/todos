#!/bin/bash

source /home/bboogaard/vens/py-todos/bin/activate && source /home/bboogaard/vens/py-todos/bin/postactivate && /home/bboogaard/vens/py-todos/bin/python /home/bboogaard/apps/py-todos/manage.py migrate --settings=app.settings-strato