"""
Test runner used by `python manage.py test`.

Our models say `managed = False` because the real tables come from
database/community_db.sql. Django therefore would NOT create those tables in
the temporary test database. This runner flips them to managed just for the
tests, so Django builds a throwaway copy of every table and deletes it after.
"""
from django.apps import apps
from django.conf import settings
from django.test.runner import DiscoverRunner


class TestRunner(DiscoverRunner):
    def setup_databases(self, **kwargs):
        for model in apps.get_models():
            model._meta.managed = True

        # A fast (insecure) password hasher, so tests run in seconds.
        settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

        return super().setup_databases(**kwargs)
