#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

cd rss_reader

sleep 5

poetry run celery -A rss_reader beat
