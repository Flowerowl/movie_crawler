# encoding: utf-8
from django.conf.urls import patterns, url

from movie_crawler.api.views.douban import MovieAPIView, CelebrityAPIView


urlpatterns = patterns('',
    url(r'^api/douban/movie/(?P<pk>[0-9]+)/$', MovieAPIView.as_view()),
    url(r'^api/douban/celebrity/(?P<pk>[0-9]+)/$', CelebrityAPIView.as_view()),
)
