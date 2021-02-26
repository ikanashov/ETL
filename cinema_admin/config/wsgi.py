"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from dotenv import load_dotenv


LOCALENVIROMENTPATH = '../../'


def load_local_env():
    envfile = LOCALENVIROMENTPATH + '.env'
    dotenv_path = os.path.join(os.path.dirname(__file__), envfile)
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    else:
        print()
        print('!!!WARNING!!!')
        print(f'Local environment file (.env) not found in path:"{LOCALENVIROMENTPATH}".')
        print('Default or docker-compose configuration will be used.')


load_local_env()
application = get_wsgi_application()
