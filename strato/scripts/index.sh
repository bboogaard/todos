#!/bin/bash

source /home/bboogaard/vens/py-todos/bin/activate && source /home/bboogaard/vens/py-todos/bin/postactivate && /home/bboogaard/vens/py-todos/bin/python /home/bboogaard/apps/py-todos/manage.py update_index --age=24 --settings=app.settings-strato

