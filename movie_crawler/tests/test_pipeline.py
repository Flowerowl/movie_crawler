# coding: utf-8
from __future__ import unicode_literals
import unittest

from scrapy.spider import Spider
from django_dynamic_fixture import G

from movie_crawler.store.mtime.models import Movie, Genre
from movie_crawler.items.mtime import MovieItem
from movie_crawler.pipelines.save import SavePipeline

class PipelineTestCase(unittest.TestCase):
    def setUp(self):
        self.spider = Spider(name="movie.mtime.com")  # FIXME: REMOVE
        self.genre = G(Genre)
        self.movie = G(Movie, genres=[self.genre])

    def test_preocess_item_add_m2m_fields(self):
        genre1 = {"title": self.genre.title}
        genre2 = {"title": "genre_title"}
        item = MovieItem(
            id=self.movie.id,
            title="movie_title",
            genres=[genre1, genre2]
        )
        SavePipeline().process_item(item=item, spider=self.spider)
        movie = Movie.objects.get(pk=self.movie.pk)
        self.assertEqual(movie.genres.count(), 2)
        self.assertEqual(movie.genres.all()[0].title, self.genre.title)
        self.assertEqual(movie.genres.all()[1].title, "genre_title")

    def test_preocess_item_remove_m2m_fields(self):
        genre = {"title": "genre_title"}
        item = MovieItem(
            id=self.movie.id,
            title="movie_title",
            genres=[genre]
        )
        SavePipeline().process_item(item=item, spider=self.spider)
        movie = Movie.objects.get(pk=self.movie.pk)
        self.assertEqual(movie.genres.count(), 1)
        self.assertEqual(movie.genres.all()[0].title, "genre_title")
