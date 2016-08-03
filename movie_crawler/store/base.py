# coding: utf-8
from __future__ import unicode_literals

from django.db import models
import jsonfield


__all__ = [
    "BaseMovie", "BaseCelebrity", "BasePhoto", "BaseGenre",
    "BaseArea", "BaseTag", "BaseAward", "BaseCompany"
]


class BaseMovie(models.Model):
    """
    电影详情
    """

    id = models.IntegerField(primary_key=True, verbose_name="电影ID")
    id_imdb = models.CharField(max_length=255, blank=True, verbose_name="IMDB ID")

    title = models.CharField(max_length=255, blank=True, verbose_name="标题")
    title_sub = models.CharField(max_length=255, blank=True, verbose_name="副标题")
    title_en = models.CharField(max_length=255, blank=True, null=True, verbose_name="英文标题")
    alias = jsonfield.JSONField(default=list, blank=True, verbose_name="别称")

    intro = models.TextField(blank=True, verbose_name="剧情")
    runtime = models.CharField(max_length=15, null=True, blank=True, verbose_name="片长", help_text="单位分钟")
    rating = models.FloatField(default=0, blank=True, verbose_name="评分")
    rating_imdb = models.FloatField(default=0, blank=True, verbose_name="IMDB评分")
    premiere = models.DateField(null=True, blank=True, verbose_name="首播日期")
    season = models.IntegerField(null=True, blank=True, verbose_name="季")
    episode = models.IntegerField(null=True, blank=True, verbose_name="集")

    language = jsonfield.JSONField(default=list, blank=True, verbose_name="语言")
    genres = models.ManyToManyField('Genre', null=True, blank=True, verbose_name="分类")
    tags = models.ManyToManyField('Tag', null=True, blank=True, verbose_name="标签")

    stars = models.ManyToManyField('Celebrity', null=True, related_name="star_movie", blank=True, verbose_name="演员")
    directors = models.ManyToManyField('Celebrity', null=True, related_name="direct_movie", blank=True, verbose_name="导演")
    writers = models.ManyToManyField('Celebrity', null=True, related_name="write_movie", blank=True, verbose_name="编剧")
    producers = models.ManyToManyField('Celebrity', null=True, related_name="product_movie", blank=True, verbose_name="制作人")
    photo_graphers = models.ManyToManyField('Celebrity', null=True, related_name="photo_movie", blank=True, verbose_name="摄影")
    editors = models.ManyToManyField('Celebrity', null=True, related_name="edit_movie", blank=True, verbose_name="剪辑")
    music_makers = models.ManyToManyField('Celebrity', null=True, related_name="music_movie", blank=True, verbose_name="音乐制作")
    production_designers = models.ManyToManyField('Celebrity', null=True, related_name="design_movie", blank=True, verbose_name="艺术指导")
    effect_artists = models.ManyToManyField('Celebrity', null=True, related_name="effect_movie", blank=True, verbose_name="特效")
    assistant_directors = models.ManyToManyField('Celebrity', null=True, related_name="assistant_movie", blank=True, verbose_name="助理导演")
    art_designers = models.ManyToManyField('Celebrity', null=True, related_name="art_movie", blank=True, verbose_name="美术设计")
    costume_designers = models.ManyToManyField('Celebrity', null=True, related_name="costume_movie", blank=True, verbose_name="服装设计")
    choreographer = models.ManyToManyField('Celebrity', null=True, related_name="choreographer_movie", blank=True, verbose_name="动作指导")

    relatives = models.ManyToManyField('self', null=True, blank=True, verbose_name="相关电影")
    company_production = models.ManyToManyField('Company', null=True, related_name="company_product_movie", blank=True, verbose_name="制作公司")
    company_release = models.ManyToManyField('Company', null=True, related_name="company_release_movie", blank=True, verbose_name="发行公司")

    year = models.IntegerField(null=True, blank=True, verbose_name="年份")
    areas = models.ManyToManyField('Area', null=True, blank=True, verbose_name="地区")
    showing_date = jsonfield.JSONField(default=list, blank=True, verbose_name="上映地区及时间")
    characters = jsonfield.JSONField(default=list, blank=True, verbose_name="角色")

    website = models.URLField(max_length=255, blank=True, verbose_name="官方网站")
    cost = models.CharField(max_length=255, blank=True, verbose_name="制作成本")
    back_story = jsonfield.JSONField(default=list, blank=True, verbose_name="幕后")
    level = models.CharField(max_length=255, blank=True, verbose_name="等级")

    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.title


class BaseCelebrity(models.Model):
    """
    艺人详情
    """

    id = models.IntegerField(primary_key=True, verbose_name="艺人ID")
    id_imdb = models.CharField(max_length=255, blank=True, verbose_name="IMDB ID")

    name = models.CharField(max_length=255, blank=True, verbose_name="中文名")
    name_en = models.CharField(max_length=500, blank=True, verbose_name="外文名")
    alias = jsonfield.JSONField(default=list, blank=True, verbose_name="别称")

    intro = models.TextField(blank=True, verbose_name="简介")
    gender = models.IntegerField(choices=((0, "男"), (1, "女"), (2, "组合")), null=True, blank=True, verbose_name="性别")
    nation = models.CharField(max_length=255, blank=True, verbose_name="民族")
    nationality = models.CharField(max_length=255, blank=True, verbose_name="国籍")
    birthplace = models.CharField(max_length=255, blank=True, verbose_name="出生地")
    birthday = models.CharField(max_length=255, blank=True, verbose_name="出生日期")
    deathday = models.CharField(max_length=255, blank=True, verbose_name="去世日期")
    weight = models.IntegerField(null=True, blank=True, verbose_name="体重(kg)")
    height = models.IntegerField(null=True, blank=True, verbose_name="身高(cm)")
    blood = models.CharField(max_length=255, null=True, blank=True, verbose_name="血型")
    isdead = models.NullBooleanField(default=False, null=True, blank=True, verbose_name="是否去世")
    constellation = models.CharField(max_length=255, blank=True, verbose_name="星座")
    professions = jsonfield.JSONField(default=list, blank=True, verbose_name="职业")
    family = jsonfield.JSONField(max_length=255, blank=True, verbose_name="家族成员")
    debut = models.DateField(null=True, blank=True, verbose_name="出道时间")
    school = models.CharField(max_length=255, blank=True, verbose_name="毕业院校")
    website = models.URLField(max_length=255, blank=True, verbose_name="官方网站")

    education = models.TextField(verbose_name="教育经历")
    works = models.TextField(verbose_name="主要作品")
    achievement = models.TextField(verbose_name="主要成就")
    experience = models.TextField(verbose_name="星路历程")

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name


class BasePhoto(models.Model):
    """
    图片
    """

    movie_id = models.IntegerField(null=True, blank=True, verbose_name="电影ID")
    celebrity_id = models.IntegerField(null=True, blank=True, verbose_name="艺人ID")

    url = models.CharField(max_length=255, verbose_name="图片URL")
    size = models.CharField(max_length=255, null=True, blank=True, verbose_name="文件大小")
    pixel = models.CharField(max_length=255, null=True, blank=True, verbose_name="分辨率")
    type = models.CharField(max_length=255, null=True, blank=True, verbose_name="图片类型(封面/官方剧照/工作照等)")
    image = models.ImageField(upload_to="photo", null=True, blank=True, verbose_name="图片文件")
    upload_time = models.DateField(null=True, blank=True, verbose_name="用户上传时间")

    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        abstract = True
        verbose_name = verbose_name_plural = "图片"

    def __unicode__(self):
        return self.image.url


class BaseGenre(models.Model):
    """
    分类
    """

    title = models.CharField(max_length=50, unique=True, verbose_name="名称")

    class Meta:
        abstract = True
        verbose_name = verbose_name_plural = "分类"

    def __unicode__(self):
        return self.title


class BaseArea(models.Model):
    """
    地区
    """

    name = models.CharField(max_length=255, unique=True, verbose_name="地区名称")
    name_en = models.CharField(max_length=255, blank=True, verbose_name="地区英文名称")

    class Meta:
        abstract = True
        verbose_name = verbose_name_plural = "地区"

    def __unicode__(self):
        return self.name


class BaseTag(models.Model):
    """
    标签
    """

    title = models.CharField(max_length=255, unique=True, verbose_name="标签名称")

    class Meta:
        abstract = True
        verbose_name = verbose_name_plural = "标签"

    def __unicode__(self):
        return self.title


class BaseAward(models.Model):
    """
    奖项
    """

    name = models.CharField(max_length=255, blank=True, verbose_name="颁奖礼名称")
    title = models.CharField(max_length=255, blank=True, verbose_name="具体奖项名称")
    year = models.IntegerField(null=True, blank=True, verbose_name="年份")
    period = models.IntegerField(null=True, blank=True, verbose_name="届")
    movies = models.ManyToManyField('Movie', null=True, blank=True, related_name='movie_award', verbose_name="电影")
    stars = models.ManyToManyField('Celebrity', null=True, blank=True, related_name='celebrity_award', verbose_name="艺人")

    class Meta:
        abstract = True
        verbose_name = verbose_name_plural = "奖项"
        unique_together = ("name", "title", "year", "period")

    def __unicode__(self):
        return '%s, %s, %s, %s' % (self.year, self.name, self.title, self.award_type)


class BaseCompany(models.Model):
    """
    电影公司
    """

    id = models.IntegerField(primary_key=True, verbose_name="公司ID")
    name = models.CharField(max_length=255, verbose_name="公司名称")
    name_en = models.CharField(max_length=255, blank=True, verbose_name="公司英文名称")
    country = models.CharField(max_length=255, blank=True,  verbose_name="公司名称")

    class Meta:
        abstract = True
        verbose_name = verbose_name_plural = "公司"

    def __unicode__(self):
        return self.name


class BaseComment(models.Model):
    """
    评论
    """

    id_comment = models.IntegerField(null=True, blank=True, verbose_name="豆瓣ID")
    id_movie = models.IntegerField(db_index=True, verbose_name="电影")
    username = models.CharField(max_length=255, verbose_name="用户")
    title = models.CharField(max_length=255, null=True, blank=True, verbose_name="标题")
    content = models.TextField(blank=True, verbose_name="内容")
    rating = models.FloatField(default=0, blank=True, verbose_name="评分")
    type = models.IntegerField(choices=((1, "短评"), (2, "长评")), null=True, blank=True, verbose_name="类型")
    like = models.IntegerField(null=True, blank=True, verbose_name="赞")
    dislike = models.IntegerField(null=True, blank=True, verbose_name="赞")
    created_time = models.DateField(null=True, blank=True, verbose_name="创建时间")

    class Meta:
        abstract = True
        verbose_name = verbose_name_plural = "评论"

    def __unicode__(self):
        return self.username
