# coding: utf-8
from __future__ import unicode_literals

from urlparse import urlparse
import os
import unittest

from scrapy.http import HtmlResponse, TextResponse, Request

from movie_crawler.spiders.douban.movie import MovieSpider
from movie_crawler.items.douban import (
    MovieItem, CelebrityItem, AwardItem, CommentItem
)


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

    def test_parse_movie_base_without_imdb(self):
        """
        @url: http://movie.douban.com/subject/1867420/
        """
        response = self.fake_response_from_file("movie_without_imdb.html", url="http://movie.douban.com/subject/1867420/")
        result = self.spider.parse_movie_base(response)
        movie = result.next()
        self.assertEqual(movie['id'], 1867420)
        self.assertEqual(movie['episode'], 26)
        self.assertEqual(movie['runtime'], '27分钟')
        self.assertEqual(movie['title'], '头文字D：First Stage 頭文字D：First Stage')
        self.assertEqual(movie['year'], 1998)
        self.assertEqual(movie['rating'], 8.7)
        self.assertEqual(movie['language'], ['英语', '日语'])
        self.assertEqual(movie['intro'].strip()[:10], "藤原豆腐店的日常业务")
        self.assertEqual(movie['alias'], ['Initial D: First Stage'])
        self.assertEqual(movie['genres'], [{'title': '喜剧'}, {'title': '动作'}, {'title': '动画'}, {'title': '运动'}])
        self.assertEqual(movie['season'], 1)
        self.assertEqual(movie['stars'], [])
        self.assertEqual(movie['website'], 'http://www.avexmovie.jp/lineup/initial/initial.html')
        self.assertEqual(movie['showing_date'], ['1998-04-18'])
        self.assertIn({'title': '1998'}, movie['tags'])
        self.assertIn({'id': 4006490}, movie['relatives'])

        self.assertEqual(result.next()['type'], 'cover')

        for award_item in [
            AwardItem(movies=[{'id': 1867420}], name='香港电影金像奖', period=25, title='最佳电影(提名)'),
            AwardItem(movies=[{'id': 1867420}], stars=[{'id': 1106979}, {'id': 1126158}], name='香港电影金像奖', period=25, title='最佳导演(提名)'),
            AwardItem(movies=[{'id': 1867420}], name='香港电影金像奖', stars=[{'id': 1050076}], period=25, title='最佳男配角'),
        ]:
            self.assertEqual(result.next(), award_item)
        for comment_id in [162267527, 616214381, 735909893, 485572374]:
            self.assertEqual(result.next()['id_comment'], comment_id)
        for review_id in [6195573, 5760401, 5480378]:
            self.assertEqual(int(result.next().url.split('/')[-2]), review_id)
        self.assertEqual(result.next().url, 'http://movie.douban.com/subject/1867420/photos')

    def test_parse_celebrity_base(self):
        """
        @url: http://movie.douban.com/celebrity/1048000/
        """
        response = self.fake_response_from_file("celebrity.html", url="http://movie.douban.com/celebrity/1048000/")
        result = self.spider.parse_celebrity(response)
        celebrity = result.next()
        self.assertEqual(celebrity['id'], 1048000)
        self.assertEqual(celebrity['website'], 'www.jvrmusic.com')
        self.assertEqual(celebrity['name'], '周杰伦 Jay Chou')
        self.assertEqual(celebrity['id_imdb'], 'nm1727100')
        self.assertEqual(celebrity['constellation'], '摩羯座')
        self.assertEqual(celebrity['birthplace'], '台湾,台北')
        self.assertEqual(celebrity['birthday'], '1979-01-18')
        self.assertEqual(celebrity['family'], ['周耀中(父)','叶惠美(母)'])
        self.assertEqual(celebrity['intro'].strip()[:10], '中国台湾华语流行歌手')
        self.assertEqual(celebrity['birthday'], '1979-01-18')
        self.assertEqual(celebrity['name_en'], ['ChouJieLun(本名)', 'PresidentChou(昵称)', 'ChowChieh-lun'])
        self.assertEqual(celebrity['professions'], ['演员', '导演', '编剧'])

        self.assertEqual(result.next()['type'], 'cover')

    def test_parse_celebrity_photo_base(self):
        """
        @url: http://movie.douban.com/celebrity/1048000/photo/826255312/
        """
        response = self.fake_response_from_file("celebrity_photo.html", url="http://movie.douban.com/celebrity/1048000/photo/826255312/")
        result = self.spider.parse_celebrity_photo_base(response)
        photo = result.next()
        self.assertEqual(photo['celebrity_id'], 1048000)
        self.assertEqual(photo['url'], 'http://img3.douban.com/view/photo/photo/public/p826255312.jpg')
        self.assertEqual(photo['pixel'], '475x473')
        self.assertEqual(photo['size'], '37.6KB')
        self.assertEqual(photo['upload_time'], '2011-01-30')

    def test_parse_movie_photo_base(self):
        """
        @url: http://movie.douban.com/photos/photo/2092045531/
        """
        response = self.fake_response_from_file("movie_photo.html", url="http://movie.douban.com/photos/photo/2092045531/")
        result = self.spider.parse_movie_photo_base(response)
        photo = result.next()
        self.assertEqual(photo['movie_id'], 1867420)
        self.assertEqual(photo['url'], 'http://img3.douban.com/view/photo/photo/public/p2092045531.jpg')
        self.assertEqual(photo['pixel'], '640x480')
        self.assertEqual(photo['size'], '28.6KB')
        self.assertEqual(photo['upload_time'], '2013-08-16')

    def test_parse_review(self):
        """
        @url:
        """
        response = self.fake_response_from_file("review.html", url="http://movie.douban.com/review/6195573/")
        response.meta['item'] = MovieItem(id=1867420)
        result = self.spider.parse_review(response)
        comment = result
        self.assertEqual(comment['id_comment'], 6195573)
        self.assertEqual(comment['title'], '这件关于我小时候的事')
        self.assertEqual(comment['content'].strip()[:10], '今天我的一个死党说她')
        self.assertEqual(comment['rating'], 5)
        self.assertEqual(comment['like'], 7)
        self.assertEqual(comment['dislike'], 0)
        self.assertEqual(comment['created_time'], '2013-08-03')
        self.assertEqual(comment['type'], 2)
