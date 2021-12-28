#!/bin/bash

coverage run --source="." --omit="tests/*" ./manage.py test --settings=app.settings-docker-test && coverage report