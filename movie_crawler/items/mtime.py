# -*- coding: utf-8 -*-
"""
关于数据的存储，采用增量更新的策略（即索引存在，则更新，索引不存在，则创建）。
因此，对于爬取数据中包含索引的对象（例如电影、艺人），直接保存即可。
对于爬取数据中不包含索引的对象（例如分类，奖项等），需要通过unique字段判断
对象是否存在。
"""

from __future__ import unicode_literals

from scrapy import Field
from scrapy.contrib.djangoitem import DjangoItem

from movie_crawler.store.mtime.models import (
    Movie, Celebrity, Genre, Area, Tag, Photo,
    Company, Award, Character
)


class MovieItem(DjangoItem):
    """
    电影详情
    """

    django_model = Movie
    unique_fields = ("id",)

    # DjangoItem MetaClass仅支持auto-create Field
    # 因此，需要手动添加所有ManyToManyField到Item中
    genres = Field()
    # photos = Field()

    stars = Field()
    directors = Field()
    writers = Field()
    producers = Field()
    photo_graphers = Field()
    editors = Field()
    music_makers = Field()
    production_designers = Field()
    effect_artists = Field()
    assistant_directors = Field()
    art_designers = Field()
    costume_designers = Field()
    choreographer = Field()

    # awards = Field()
    relatives = Field()
    company_production = Field()
    company_release = Field()

    # area = Field()


class CelebrityItem(DjangoItem):
    """
    艺人详情
    """
    django_model = Celebrity
    unique_fields = ("id",)


class CompanyItem(DjangoItem):
    """
    公司
    """
    django_model = Company
    unique_fields = ("id",)


class CharacterItem(DjangoItem):
    """
    角色
    """
    django_model = Character
    unique_fields = ("movie", "character",)


class PhotoItem(DjangoItem):
    """
    图片
    """
    django_model = Photo


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
    unique_fields = ("name", "title", "year", "period", "award_type",)


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
