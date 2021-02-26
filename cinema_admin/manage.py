#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

from dotenv import load_dotenv

LOCALENVIROMENTPATH = '../'


def load_local_env():
    envfile = LOCALENVIROMENTPATH + '.env'
    dotenv_path = os.path.join(os.path.dirname(__file__), envfile)
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    else:
        print()
        print('!!!WARNING!!!')
        print(f'Local environment file (.env) not found in path:"{LOCALENVIROMENTPATH}".')
        print('Default configuration will be used.')


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
    load_local_env()
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
