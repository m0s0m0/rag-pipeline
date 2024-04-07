#!/bin/sh
celery -A post_analyzer worker -P threads --loglevel=info 