# coding: utf-8
from __future__ import unicode_literals

from rest_framework.generics import RetrieveAPIView

from movie_crawler.store.douban.models import Movie, Celebrity


class MovieAPIView(RetrieveAPIView):
    """
    `电影`接口
    """
    model = Movie


class CelebrityAPIView(RetrieveAPIView):
    """
    `艺人`接口
    """
    model = Celebrity
