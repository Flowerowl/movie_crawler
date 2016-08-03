#coding:utf-8
from .django_settings import *  # NOQA


DEV_DATABASES = {
    'douban': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'douban.sqlite3'),
    },
    'mtime': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'mtime.sqlite3'),
    }
}

DATABASES = DEV_DATABASES
