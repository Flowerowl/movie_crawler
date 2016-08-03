# coding: utf-8
from __future__ import unicode_literals


APP_DB = {
    'mtime':  'mtime',
    'douban': 'douban',
}


class StoreAppRouter(object):
    """
    A router to control all database operations on models in the
    storage application.
    """
    def db_for_read(self, model, **hints):
        if model._meta.app_label in APP_DB:
            return APP_DB[model._meta.app_label]
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in APP_DB:
            return APP_DB[model._meta.app_label]
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label in APP_DB or \
                obj2._meta.app_label in APP_DB:
            return True
        return None

    def allow_syncdb(self, db, model):
        if db == APP_DB.get(model._meta.app_label):
            return True
        elif model._meta.app_label in APP_DB:
            return False
        return None
