# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from scrapy import Field
from scrapy.contrib.djangoitem import DjangoItem

from movie_crawler.store.douban.models import (
    Movie, Celebrity, Genre, Area,
    Tag, Photo, Award, Comment
)


class MovieItem(DjangoItem):
    """
    电影详情
    """

    django_model = Movie
    unique_fields = ('id',)

    # DjangoItem MetaClass仅支持auto-create Field
    # 因此，需要手动添加所有ManyToManyField到Item中
    genres = Field()
    tags = Field()
    areas = Field()
    stars = Field()
    directors = Field()
    writers = Field()
    relatives = Field()
    comments = Field()


class CelebrityItem(DjangoItem):
    """
        艺人详情
    """

    django_model = Celebrity
    unique_fields = ('id',)


class CommentItem(DjangoItem):
    """
        评论
    """

    django_model = Comment
    unique_fields = ('id_movie', 'id_comment', 'type')


class PhotoItem(DjangoItem):
    """
        图片
    """

    django_model = Photo
    unique_fields = ('url',)


class GenreItem(DjangoItem):
    """
    分类
    """
    django_model = Genre
    unique_fields = ("title",)


class AwardItem(DjangoItem):
    """
    奖项
    """
    django_model = Award
    unique_fields = ("name", "title", "year", "period",)

    stars = Field()
    movies = Field()


class TagItem(DjangoItem):
    """
    标签
    """
    django_model = Tag
    unique_fields = ("title",)


class AreaItem(DjangoItem):
    """
    地区
    """
    django_model = Area
    unique_fields = ("name",)
