#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

cd rss_reader

# wait for the django application to start
while [[ "$(curl -s -o /dev/null -w ''%{http_code}'' web:8000/admin)" != 301 ]]; do sleep 5; done

# run the worker and scheduler together
poetry run celery -A rss_reader worker -l info -B
