# coding: utf-8
from __future__ import unicode_literals

from django.db import models

from movie_crawler.store.base import *
from movie_crawler.store.base import BaseComment


class Movie(BaseMovie):
    pass

class Celebrity(BaseCelebrity):
    pass

class Photo(BasePhoto):
    pass

class Genre(BaseGenre):
    pass

class Area(BaseArea):
    pass

class Tag(BaseTag):
    pass

class Award(BaseAward):
    pass

class Company(BaseCompany):
    pass

class Comment(BaseComment):
    pass

class Character(models.Model):
    """
    电影角色
    """
    movie = models.IntegerField(verbose_name="电影ID")
    character = models.CharField(max_length=255, null=True, blank=True, verbose_name="角色名称")
    celebrity = models.IntegerField(null=True, blank=True, verbose_name="演员ID")

    class Meta:
        unique_together = ('movie', 'character')
        verbose_name = verbose_name_plural = "电影角色"
