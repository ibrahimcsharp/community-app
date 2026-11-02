"""
Let Django 5.2 work with MariaDB 10.4 (the version that ships with XAMPP).

Django 5.2 officially supports MariaDB 10.5 and newer. Two things stop it
from working with 10.4, and we switch both off here:

  1. Django refuses to connect to anything older than 10.5.
     -> we lower that minimum to 10.4.

  2. On MariaDB, Django saves new rows with "INSERT ... RETURNING id".
     MariaDB only learned RETURNING in 10.5, so on 10.4 every insert fails.
     -> we tell Django to use the older way (insert, then ask for the new id).

If you upgrade to MariaDB 10.5+ or MySQL 8, delete this file and the
import line for it in config/__init__.py. Nothing else needs to change.
"""
from django.db.backends.mysql.features import DatabaseFeatures

DatabaseFeatures.minimum_database_version = (10, 4)
DatabaseFeatures.can_return_columns_from_insert = False
