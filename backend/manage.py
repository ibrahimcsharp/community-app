#!/usr/bin/env python
"""Django's command-line tool. Examples:

    python manage.py runserver            start the API on http://127.0.0.1:8000
    python manage.py migrate              create Django's own helper tables
    python manage.py test                 run the tests
    python manage.py changepassword sara  set a new password for a user
"""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
