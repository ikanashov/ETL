#!/bin/sh

uwsgi --chdir=/cinema_admin \
    --http :${DJANGO_PORT} \
    --module=config.wsgi \
    --env DJANGO_SETTINGS_MODULE=config.settings.dev \
    --processes=5 \
    --uid=1000 --gid=2000 \
    --harakiri=20 \
    --max-requests=5000 \
    --check-static /cinema_admin/config \
    --vacuum
