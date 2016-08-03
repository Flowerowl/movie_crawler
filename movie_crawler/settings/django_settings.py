# coding: utf-8
from importlib import import_module
import os


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATABASE_ROUTERS = ['movie_crawler.settings.db_router.StoreAppRouter', ]

# 配置INSTALLED_APPS
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'movie_crawler.api',
    'movie_crawler.store.douban',
    'movie_crawler.store.mtime',

    'rest_framework',
)

SECRET_KEY = '%0d8h3=aa+rv*-p45uz^htr27ajh_(50w$*z=i6_c08w6$zbj6'

DEBUG = True
TEMPLATE_DEBUG = True
ALLOWED_HOSTS = []
APPEND_SLASH = True

#MIDDLEWARE_CLASSES = (
    #'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    #'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.contrib.messages.middleware.MessageMiddleware',
    #'django.middleware.clickjacking.XFrameOptionsMiddleware',
#)


ROOT_URLCONF = 'movie_crawler.api.urls'
WSGI_APPLICATION = 'movie_crawler.wsgi.application'


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_L10N = True
USE_TZ = True

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, "templates"),
)
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',

)

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)
