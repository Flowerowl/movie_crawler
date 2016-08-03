# coding: utf-8
from __future__ import unicode_literals
from urlparse import urlparse
import os
import unittest

from scrapy.http import HtmlResponse, TextResponse, Request
from selenium import webdriver

from movie_crawler.spiders.mtime.movie import MovieSpider, SeleniumSpider
from movie_crawler.items.mtime import MovieItem, CharacterItem, CelebrityItem


class SpiderTestCase(unittest.TestCase):
    def setUp(self):
        self.spider = MovieSpider()
        self.html_dir = os.path.join(os.path.dirname(__file__), "html")

    def fake_response_from_file(self, filename, meta=None, url="http://www.test.com"):
        with open(os.path.join(self.html_dir, filename)) as f:
            html = f.read()
        request = Request(url=url, meta=meta)
        response = HtmlResponse(url=url, body=html, request=request)
        return response

    def test_parse_movie_rating(self):
        """
        @url: http://service.library.mtime.com/Movie.api?Ajax_CallBack=true&
              Ajax_CallBackType=Mtime.Library.Services&Ajax_CallBackMethod=G
              etMovieOverviewRating&Ajax_CrossDomain=1&Ajax_RequestUrl=http%
              3A%2F%2Fmovie.mtime.com%2F12135%2F&t=20148715112823067&Ajax_Ca
              llBackArgument0=12135
        """
        url = "http://www.test.com"
        body = ('var result_20148715112823067 = { "value":{"isRelease":true,"'
        'movieRating":{"MovieId":12135,"RatingFinal":6.9,"RDirectorFinal":7.'
        '9,"ROtherFinal":7.9,"RPictureFinal":8.3,"RShowFinal":7.5,"RStoryFin'
        'al":7.1,"RTotalFinal":7.4,"Usercount":112467,"AttitudeCount":9207},'
        '"movieTitle":"卧虎藏龙","tweetId":0,"userLastComment":"","userLastCo'
        'mmentUrl":"","releaseType":3},"error":null};var movieOverviewRating'
        'Result=result_20148715112823067;')
        request = Request(url=str(url), meta={"movie": MovieItem(id=12135)})
        response = TextResponse(url=str(url), body=body, encoding="utf-8", request=request)

        result = self.spider.parse_movie_rating(response)
        self.assertEqual(result.next(), MovieItem(id=12135, rating=6.9))

    def test_parse_movie_rating_with_id_none(self):
        url = "http://www.test.com"
        body = ('var result_20148715112823067 = { "value":{"isRelease":true,"'
        'movieRating":{"RatingFinal":6.9,"RDirectorFinal":7.'
        '9,"ROtherFinal":7.9,"RPictureFinal":8.3,"RShowFinal":7.5,"RStoryFin'
        'al":7.1,"RTotalFinal":7.4,"Usercount":112467,"AttitudeCount":9207},'
        '"movieTitle":"卧虎藏龙","tweetId":0,"userLastComment":"","userLastCo'
        'mmentUrl":"","releaseType":3},"error":null};var movieOverviewRating'
        'Result=result_20148715112823067;')
        request = Request(url=str(url), meta={"movie": MovieItem(id=12135)})
        response = TextResponse(url=str(url), body=body, encoding="utf-8", request=request)

        result = self.spider.parse_movie_rating(response)
        self.assertEqual(result.next(), None)

    def test_parse_movie_credits(self):
        """
        @url: http://movie.mtime.com/157125/fullcredits.html
        """
        response = self.fake_response_from_file("fullcredits.html")
        response.meta["item"] = MovieItem(id=1)

        result = self.spider.parse_movie_credits(response)
        for url in [
            "http://people.mtime.com/923349/",
            "http://people.mtime.com/923349/",
            "http://people.mtime.com/1123707/",
            "http://people.mtime.com/2007533/",
            "http://people.mtime.com/1206936/",
            "http://people.mtime.com/1965952/",
            "http://people.mtime.com/1485748/",
            "http://people.mtime.com/892852/",
            "http://people.mtime.com/1557633/",
            "http://people.mtime.com/1279236/",
            "http://people.mtime.com/1951520/",
        ]:
            self.assertEqual(url, result.next().url)

        for character_item in [
            CharacterItem(celebrity=1646888, character='郑微', movie=1),
            CharacterItem(celebrity=1248957, character='黎维娟', movie=1),
        ]:
            self.assertEqual(result.next(), character_item)

        for url in [
            "http://people.mtime.com/1646888/",
            "http://people.mtime.com/1248957/"
        ]:
            self.assertEqual(result.next().url, url)

        item = result.next()
        self.assertEqual(item['id'], 1)
        self.assertEqual(item['directors'], [{u'id': 923349}, {u'id': 923349}])
        self.assertEqual(item['editors'], [{u'id': 1279236}])
        self.assertEqual(item['music_makers'], [{u'id': 1951520}])
        self.assertEqual(item['photo_graphers'], [{'id': 1557633}])
        self.assertEqual(item['producers'], [
            {'id': 1206936},
            {'id': 1965952},
            {'id': 1485748},
            {'id': 892852},
        ])
        self.assertEqual(item['stars'], [{'id': 1646888}, {'id': 1248957}])
        self.assertEqual(item['writers'], [{'id': 1123707}, {'id': 2007533}])

    def test_parse_movie_plots(self):
        response = self.fake_response_from_file("plots.html")
        response.meta["item"] = MovieItem(id=1)

        result = self.spider.parse_movie_plots(response)
        item = result.next()
        self.assertEqual(item["id"], 1)
        self.assertEqual(item["intro"], "\n\n".join(["ab", "cd", "ef"]))

    def test_parse_movie_detail(self):
        """
        @url: http://movie.mtime.com/157125/details.html
        """
        response = self.fake_response_from_file("details.html")
        response.meta["item"] = MovieItem(id=1)

        result = self.spider.parse_movie_detail(response)

        for url in [
            "http://movie.mtime.com/company/2599/",
            "http://movie.mtime.com/company/103225/",
            "http://movie.mtime.com/company/57839/",
            "http://movie.mtime.com/company/82305/",
            "http://movie.mtime.com/company/100077/",
            "http://movie.mtime.com/company/112082/",
            "http://movie.mtime.com/company/114543/",
            "http://movie.mtime.com/company/114547/",
            "http://movie.mtime.com/company/114548/",
            "http://movie.mtime.com/company/57839/",
            "http://movie.mtime.com/company/2599/",
        ]:
            self.assertEqual(url, result.next().url)

        item = result.next()
        self.assertEqual(item["id"], 1)
        self.assertEqual(item["alias"], ["致青春", "To Our Youth That To Fading Away"])
        self.assertEqual(item["language"], ["汉语普通话"])
        self.assertEqual(item["showing_date"], {
            "中国": "2013年4月26日",
        })
        self.assertEqual(item["company_production"], [
            {u'id': 2599},
            {u'id': 103225},
            {u'id': 57839},
            {u'id': 82305},
            {u'id': 100077},
            {u'id': 112082},
            {u'id': 114543},
            {u'id': 114547},
            {u'id': 114548}
        ])
        self.assertEqual(item["company_release"], [{u'id': 57839}, {u'id': 2599}])

    def test_parse_celebrity(self):
        """
        @url: http://people.mtime.com/914002/
        """
        response = self.fake_response_from_file("celebrity.html", url="http://people.mtime.com/914002/")
        result = self.spider.parse_celebrity(response)

        request = result.next()
        self.assertEqual(request.url, "http://people.mtime.com/914002/details.html")
        request = result.next()
        self.assertEqual(request.url, "http://people.mtime.com/914002/awards.html")
        celebrity_item = result.next()
        self.assertEqual(celebrity_item["id"], 914002)
        self.assertEqual(celebrity_item["name"], "拉尔夫·费因斯")
        self.assertEqual(celebrity_item["name_en"], "Ralph Fiennes")

    def test_parse_celebrity_detail(self):
        """
        @url: http://people.mtime.com/914002/details.html
        """
        meta = {"celebrity": CelebrityItem(id=914002)}
        response = self.fake_response_from_file("celebrity_detail.html", meta=meta)

        celebrity_item = self.spider.parse_celebrity_detail(response)
        self.assertEqual(celebrity_item["birthday"], "1962-12-22")
        self.assertEqual(celebrity_item["birthplace"], "英国萨福克郡")
        self.assertEqual(celebrity_item["height"], 183)
        self.assertEqual(celebrity_item["constellation"], "魔羯座")

    def test_parse_celebrity_awards(self):
        """
        @url: http://people.mtime.com/914002/awards.html
        """
        pass


class SeleniumSpiderTestCase(unittest.TestCase):
    def setUp(self):
        self.spider = SeleniumSpider()

    def tearDown(self):
        filename = SeleniumSpider.last_crawl_point_filename
        if os.path.exists(filename):
            os.remove(filename)
        if self.spider._browser:
            self.spider._browser.quit()

    def test_parse_movie_list_by(self):
        return
        for movie in self.spider.crawl_movie_list_by(genre_value=192, genre_index=0, page=1):
            pass

    def test_save_last_crawl_point(self):
        SeleniumSpider.save_last_crawl_point(genre_dom_index=1, page=2)
        filename = SeleniumSpider.last_crawl_point_filename
        with open(filename) as f:
            self.assertEqual(f.read(), "1::2")
        SeleniumSpider.save_last_crawl_point(genre_dom_index=3, page=4)
        with open(filename) as f:
            self.assertEqual(f.read(), "3::4")

    def test_get_last_crawl_point(self):
        self.assertEqual(SeleniumSpider.get_last_crawl_point(), (0, 1))

        filename = SeleniumSpider.last_crawl_point_filename
        with open(filename, "w") as f:
            f.write("1::2")
        self.assertEqual(SeleniumSpider.get_last_crawl_point(), (1, 2))

    def test_change_proxy_with_no_proxy(self):
        proxy_args = self.spider._change_proxy()
        self.spider._browser = webdriver.PhantomJS(service_args=proxy_args)
        self.assertTrue(self.spider._proxy + "\n" in self.spider._proxy_middleware.proxies)

    def test_change_proxy_with_proxy(self):
        o = urlparse(self.spider._proxy_middleware.proxies[0])
        proxy_args = [
            '--proxy={}'.format(o.netloc.strip()),
            '--proxy-type={}'.format(o.scheme),
        ]
        self.spider._browser = webdriver.PhantomJS(service_args=proxy_args)
        old_proxy = self.spider._proxy

        proxy_args = self.spider._change_proxy()
        self.spider._browser = webdriver.PhantomJS(service_args=proxy_args)
        new_proxy = self.spider._proxy

        self.assertTrue(old_proxy + "\n" not in self.spider._proxy_middleware.proxies)
        self.assertTrue(new_proxy + "\n" in self.spider._proxy_middleware.proxies)
