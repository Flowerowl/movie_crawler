# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor

from movie_crawler.settings.scrapy_settings import PROXY_LIST


class ProxySpider(CrawlSpider):
    """
        代理爬虫, 获取最新代理, PROTOCOL://IP:PORT
    """

    name = "proxy"
    allowed_domains = ["checkerproxy.net"]
    start_urls = [
        "http://checkerproxy.net/all_proxy",
    ]
    rules = [Rule(LinkExtractor(allow=['/all_proxy$']), 'parse_proxy', follow=True)]

    def parse_proxy(self, response):
        address_set = set()
        sel = response.xpath('/html')
        ip_count = len(sel.css('#result-box-table > tbody > tr'))
        for i in range(1, ip_count):
            ip_port = sel.css('#result-box-table > tbody > tr:nth-child(%d) > td.proxy-ipport::text' % i).extract()[0]
            protocol = sel.css('#result-box-table > tbody > tr:nth-child(%d) > td.proxy-type-1::text' % i).extract()[0]
            if ip_port.split(':')[-1].isdigit():
                address = protocol.lower() + '://' + ip_port
                address_set.add(address)
            if i == 2000:
                break

        with open(PROXY_LIST, 'w') as f:
            for address in list(address_set):
                f.write(address + '\n')
