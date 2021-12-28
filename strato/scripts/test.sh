#!/bin/bash

coverage run --source="." --omit="tests/*" source /home/bboogaard/vens/py-todos/bin/activate && source /home/bboogaard/vens/py-todos/bin/postactivate && /home/bboogaard/vens/py-todos/bin/python /home/bboogaard/apps/py-todos/manage.py test --settings=app.settings-test && coverage report