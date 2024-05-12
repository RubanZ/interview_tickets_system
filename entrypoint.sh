#!/bin/sh

# Run flask migration
flask --app=app.main db upgrade

# Run the application
uwsgi --http 0.0.0.0:5000 --master -p 4 -w app.main:app