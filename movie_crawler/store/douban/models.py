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
