# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import random
import base64

from scrapy import log

from movie_crawler.settings import scrapy_settings


class ProxyMiddleware(object):
    """
        随机代理
        ref: https://github.com/aivarsk/scrapy-proxies/blob/master/randomproxy.py
    """

    def __init__(self, settings=scrapy_settings):
        try:
            self.proxy_list = settings.get('PROXY_LIST')
        except AttributeError:
            self.proxy_list = settings.PROXY_LIST

        with open(self.proxy_list) as fin:
            self.proxies = fin.readlines()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        if 'proxy' in request.meta:
            return

        proxy_address = self.get_random_proxy()
        log.msg('Proxies num: %d' % len(self.proxies))

        request.meta['proxy'] = proxy_address
        basic_auth = 'Basic ' + base64.encodestring(proxy_address)
        request.headers['Proxy-Authorization'] = basic_auth

    def process_exception(self, request, exception, spider):
        proxy = request.meta['proxy']
        try:
            self.del_proxy(proxy)
        except ValueError:
            pass

    def get_random_proxy(self):
        return random.choice(self.proxies)

    def del_proxy(self, proxy):
        if not proxy.endswith("\n"):
            proxy += "\n"
        del self.proxies[self.proxies.index(proxy)]
