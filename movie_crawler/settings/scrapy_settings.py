# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys


BASE_DIR = os.path.abspath(os.path.join(__file__, "../../"))

# Setup `DJANGO_SETTINGS_MODULE` and PYTHONPATH for django models
# http://doc.scrapy.org/en/latest/topics/djangoitem.html#django-settings-set-up
sys.path.append(BASE_DIR)

profile = os.environ.setdefault("movie_crawler_PROFILE", "dev")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movie_crawler.settings.%s" % profile)

BOT_NAME = 'movie_crawler'

SPIDER_MODULES = [
    'movie_crawler.spiders.douban',
    'movie_crawler.spiders.mtime',
    'movie_crawler.spiders.proxy'
]


DUPEFILTER_DEBUG = False

DOWNLOAD_TIMEOUT = 60
DOWNLOAD_DELAY = 2
DOWNLOADER_MIDDLEWARES = {
    # 'movie_crawler.middlewares.useragent.UserAgentMiddleware': 100,
    # 'movie_crawler.middlewares.proxy.ProxyMiddleware': 101,
    # 'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
}

PROXY_LIST = os.path.join(os.path.dirname(__file__), '..', 'proxy_list.txt')

ITEM_PIPELINES = {
    'movie_crawler.pipelines.save.SavePipeline': 100,
}

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.54 Safari/536.5'
COOKIES_ENABLED = True
HTTPCACHE_ENABLED = False

DEPTH_STATS_VERBOSE = True

EXTENSIONS = {
    "scrapy_sentry.extensions.Errors":10,
}
