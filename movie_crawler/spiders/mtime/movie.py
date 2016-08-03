# coding: utf-8
from __future__ import unicode_literals
from urlparse import urljoin, urlparse, urlunparse
from datetime import datetime
import time
import json
import os

from scrapy import log
from scrapy import Request
from scrapy.spider import Spider
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

from movie_crawler.items.mtime import MovieItem, CharacterItem, GenreItem, CelebrityItem
from movie_crawler.middlewares.proxy import ProxyMiddleware
from movie_crawler.utils import DictIgnoreSpace


class MovieSpider(Spider):
    """
    时光网电影爬虫
    """

    name = "mtime_movie"
    start_urls = [
        "http://movie.mtime.com/movie/search/section",
    ]
    rating_jsonp_url = ("http://service.library.mtime.com/Movie.api?Ajax_CallBack=true&"
    "Ajax_CallBackType=Mtime.Library.Services&Ajax_CallBackMethod=GetMovieOverviewRating&"
    "Ajax_CrossDomain=1&Ajax_RequestUrl=http%3A%2F%2Fmovie.mtime.com%2F12468%2F&t=2014871"
    "137882676&Ajax_CallBackArgument0={movie_id}")


    def __init__(self, *args, **kwargs):
        self.selenium_spider = SeleniumSpider()
        super(MovieSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        """
        入口函数，解析电影类型
        """
        log.start(logfile="mtime.movie.log", loglevel=log.DEBUG, logstdout=True)
        genre_index, page = SeleniumSpider.get_last_crawl_point()

        for genre_title in response.css("div#typePickerRegion a::text").extract():
            yield GenreItem(title=genre_title)

        for genre_value in response.css("div#typePickerRegion a::attr(cvalue)").extract()[genre_index:]:
            for movie in self.selenium_spider.crawl_movie_list_by(genre_value, genre_index, page):
                yield Request(movie, callback=self.parse_movie_base)
            genre_index += 1
            page = 1

    def _parse_id(self, url):
        return int(os.path.basename(url.rstrip("/")))

    def parse_movie_base(self, response):
        """
        爬取电影基本信息
        """
        item = MovieItem()
        sel = Selector(response)
        detail = sel.css("div.db_topcont")

        item["id"] = self._parse_id(response.url)
        item["title"] = detail.css("h1::text").extract()[0]

        title_en = detail.css("p.db_enname::text").extract()
        item["title_en"] = title_en[0] if title_en else None

        year = detail.css("p.db_year a::text").extract()
        item["year"] = int(year[0]) if year else None

        runtime = detail.css('span[property="v:runtime"]::text')
        item["runtime"] = runtime[0] if runtime else None

        genres = detail.css('a[property="v:genre"]::text').extract()
        item["genres"] = [{"title": genre} for genre in genres]

        # TODO: yield item after all other requests done
        yield item

        yield Request(
            url=self.rating_jsonp_url.format(movie_id=item["id"]),
            callback=self.parse_movie_rating,
            meta={"movie": item.copy()}
        )

        requests = [
            Request(urljoin(response.url, "fullcredits.html"), callback=self.parse_movie_credits),
            Request(urljoin(response.url, "details.html"), callback=self.parse_movie_detail),
            Request(urljoin(response.url, "plots.html"), callback=self.parse_movie_plots),
            Request(urljoin(response.url, "behind_the_scene.html"), callback=self.parse_movie_story),
        ]
        for request in requests:
            request.meta["item"] = item.copy()
            yield request

    def parse_movie_rating(self, response):
        """
        爬取电影评分
        """
        movie = response.meta["movie"]

        response_body = response.body_as_unicode()
        json_obj = '{%s}' % response_body.split('{', 1)[1].rsplit('}', 1)[0]
        obj = json.loads(json_obj).get("value").get("movieRating")

        if obj:
            id, rating = obj.get("MovieId"), obj.get("RatingFinal")
            if movie["id"] == id:
                movie["rating"] = rating
                yield movie
        yield None

    def parse_movie_credits(self, response):
        """
        爬取电影演职人员
        """
        movie = response.meta["item"]
        sel = Selector(response)

        title_to_field = DictIgnoreSpace({
            "导演 Director": "directors",
            "编剧 Writer": "writers",
            "制作人 Produced by": "producers",
            "摄影 Cinematography": "photo_graphers",
            "剪辑 Film Editing": "editors",
            "原创音乐 Original Music": "music_makers",
            "艺术指导 Production Designer": "production_designers",
            "美术设计 Art Direction by": "art_designers",
            "服装设计 Costume Design by": "costume_designers",
            "视觉特效 Visual Effects Supervisor": "effect_artists",
            "副导演/助理导演 Assistant Director": "assistant_directors",
            "动作指导 Choreographer": "choreographer",
        })

        # 爬取幕后人员
        for credits in sel.css('div.credits_list'):
            title = credits.css('h4::text').extract()[0]
            field = title_to_field[title]
            movie[field] = []
            for url in credits.css('a::attr(href)').extract():
                movie[field].append({"id": self._parse_id(url)})
                yield Request(url, callback=self.parse_celebrity)

        # 爬取角色
        for e in sel.css("div.db_actor dd"):
            character = e.css('div.character_tit h3::text').extract()
            actor = e.css('div.actor_tit h3 a::attr(href)').extract()
            yield CharacterItem(
                movie=movie["id"],
                character=character[0] if character else None,
                celebrity=self._parse_id(actor[0]) if actor else None,
            )

        # 爬取演员
        movie["stars"] = []
        for url in sel.css('div.actor_tit h3 a::attr(href)').extract():
            if url:
                movie["stars"].append({"id": self._parse_id(url)})
                yield Request(url, callback=self.parse_celebrity)

        yield movie

    def parse_celebrity(self, response):
        """
        爬取艺人
        """
        celebrity = CelebrityItem()
        sel = Selector(response)

        celebrity["id"] = self._parse_id(response.url)
        name = sel.css("div.per_header h2::text").extract()
        celebrity["name"] = name[0] if name else ""
        name_en = sel.css("div.per_header p.enname::text").extract()
        celebrity["name_en"] = name_en[0] if name_en else ""

        yield Request(
            url=urljoin(response.url, "details.html"),
            callback=self.parse_celebrity_detail,
            meta={"celebrity": celebrity.copy()}
        )
        yield Request(
            url=urljoin(response.url, "awards.html"),
            callback=self.parse_celebrity_awards,
            meta={"celebrity": celebrity.copy()}
        )

        yield celebrity

    def parse_celebrity_detail(self, response):
        """
        爬取艺人详情
        """
        celebrity = response.meta["celebrity"]
        sel = Selector(response)

        for dt in sel.css("div.per_info_l dt"):
            title = dt.css("::text").extract()[0]
            if title == "出生日期：":
                text = dt.css("::text").extract()[1].rstrip("）")
                if "（" in text:
                    birthday, birthplace = text.split("（", 1)
                else:
                    birthday, birthplace = text, ""
                celebrity["birthday"] = birthday
                celebrity["birthplace"] = birthplace
            elif title == "血型：":
                celebrity["blood"] = dt.css("::text").extract()[1]
            elif title == "星座：":
                celebrity["constellation"] = dt.css("::text").extract()[1]
            elif title == "身高：":
                celebrity["height"] = int(dt.css("::text").extract()[1].rstrip("cm"))
            elif title == "体重：":
                celebrity["height"] = int(dt.css("::text").extract()[1].rstrip("kg"))

        celebrity["intro"] = "\n".join(sel.css("div#lblAllGraphy p::text").extract())
        return celebrity

    def parse_celebrity_awards(self, response):
        """
        爬取艺人荣誉奖项
        """
        pass

    def parse_movie_detail(self, response):
        """
        爬取电影详情
        """
        movie = response.meta["item"]
        sel = Selector(response)

        # 爬取别名，对白语言以及官方网站
        movie["alias"] = []
        for dd in sel.css("div.db_movieother_2 dd"):
            title = dd.css("strong::text").extract()[0]
            if title in ["更多中文名：", "更多外文名："]:
                movie["alias"].extend([
                    name.strip(". ")
                    for name in dd.css("p::text").extract() if name.strip()
                ])
            elif title == "对白语言：":
                movie["language"] = [txt.strip() for txt in dd.css("a::text").extract()]
            elif title == "官方网站：":
                movie["website"] = dd.css("a::attr(href)").extract()

        # 爬取上映地区以及日期
        movie["showing_date"] = {}
        for li in sel.css("dl#releaseDateRegion li"):
            country = li.css("div.countryname p::text").extract()
            date = li.css("div.datecont::text").extract()
            if country and date:
                country = country[0].strip()
                date = date[0].strip()
                movie["showing_date"][country] = date

        # 爬取制作发行公司
        for div in sel.css("dl#companyRegion div.fl.wp49"):
            title = div.css("h4::text").extract()[0]
            company_urls = div.css("li a::attr(href)").extract()
            company_ids = [
                {"id": self._parse_id(url)}
                for url in company_urls
            ]
            if title == "制作公司":
                movie["company_production"] = company_ids
            elif title == "发行公司":
                movie["company_release"] = company_ids
            for url in company_urls:
                yield Request(url=url, callback=self.parse_company)

        # 爬取关联电影
        movie["relatives"] = []
        for url in sel.css("div#releatedMoviesRegion h3 a::attr(href)").extract():
            movie["relatives"].append(
                {"id": self._parse_id(url)}
            )
            yield Request(url=url, callback=self.parse_movie_base)

        yield movie

    def parse_movie_photos(self, response):
        """
        爬取电影剧照
        """
        pass

    def parse_movie_plots(self, response):
        """
        爬取电影剧情
        """
        movie = response.meta["item"]
        sel = Selector(response)
        paragraphs = []

        for paragraph in sel.css("div#paragraphRegion div.plots_box"):
            first_letter = paragraph.css("p span.first_letter::text").extract()[0]
            other_letter = "".join(paragraph.css("p::text").extract())
            paragraphs.append(first_letter + other_letter)

        movie["intro"] = "\n\n".join(paragraphs)
        yield movie

    def parse_movie_story(self, response):
        """
        爬取电影幕后花絮
        """
        pass

    def parse_company(self, response):
        """
        爬取制作/发行公司
        """
        pass


class SeleniumSpider(object):
    """
    电影列表爬虫

    外部接口：
    - crawl_movie_list_by(genre, page)
    - save_last_crawl_point(genre_dom_index, page)
    - get_last_crawl_point()
    """

    page_load_timeout = 30
    start_url = "http://movie.mtime.com/movie/search/section/#viewType=1&type={genre_value}&pageIndex={page}"
    last_crawl_point_filename = ".lastcrawl"

    def __init__(self):
        self._browser = None
        self._proxy_middleware = ProxyMiddleware()

    def crawl_movie_list_by(self, genre_value, genre_index, page=1):
        self.start_browser()
        reload_page = True

        while True:
            log.msg("Loading Page [%s]" % page)
            try:
                if reload_page:
                    self._browser.get(self._get_url(genre_value, page))
                # Waiting for page loaded
                WebDriverWait(self._browser, 60).until(
                    lambda x: x.find_element_by_css_selector("div#pagerRegion a.on").text == str(page)
                )
            except TimeoutException:
                log.msg("May be encounter captcha, save screenshot [%s]" % self._save_screenshot(), level=log.WARNING)
                proxy_args = self._change_proxy()
                self.restart_browser(service_args=proxy_args)
                reload_page = True
            except Exception as e:
                log.msg("Unknow exception [%s], save screenshot [%s]" % (e, self._save_screenshot()), level=log.ERROR)
            else:
                reload_page = False

                for e in self._browser.find_elements_by_css_selector("div#searchResultRegion a"):
                    yield e.get_attribute("href")

                SeleniumSpider.save_last_crawl_point(genre_index, page)
                try:
                    next_page = self._browser.find_element_by_id("key_nextpage")
                except NoSuchElementException:
                    self._browser.quit()
                    break
                else:
                    next_page.click()
                    page += 1

    @classmethod
    def get_last_crawl_point(cls):
        """
        获得最后一次爬取电影列表的位置
        爬取位置包含两个维度：
        1. 电影类型Dom元素在父元素中的序号
        2. 目标类型页中，电影列表的页码
        """
        genre_dom_index = 0
        page = 1
        if os.path.exists(cls.last_crawl_point_filename):
            with open(cls.last_crawl_point_filename, "r") as f:
                genre_dom_index, page = f.read().split("::")
        return int(genre_dom_index), int(page)

    @classmethod
    def save_last_crawl_point(cls, genre_dom_index, page):
        """
        保存最后一次爬取电影列表的位置

        TODO:
        将此接口迁移到MovieSpider
        """
        with open(cls.last_crawl_point_filename, "w") as f:
            f.write("{}::{}".format(genre_dom_index, page))

    def start_browser(self, **options):
        log.msg("Start browser with proxy [%s]" % options)

        self._browser = webdriver.PhantomJS(**options)
        self._browser.set_page_load_timeout(self.page_load_timeout)
        log.msg("Start browser successfully")

    def quit_browser(self):
        log.msg("Quit browser...")
        self._browser.quit()

    def restart_browser(self, **options):
        self.quit_browser()

        time.sleep(2)
        self.start_browser(**options)

    @property
    def _proxy(self):
        if self._browser:
            service_args = self._browser.service.service_args
            if service_args[1].startswith("--proxy="):
                netloc = service_args[1].split("=")[1]
                scheme = service_args[2].split("=")[1]
                return urlunparse((scheme, netloc, "", "", "", ""))
        return ""

    def _change_proxy(self):
        """
        获得新的浏览器代理参数
        """
        old_proxy = self._proxy
        new_proxy = self._proxy_middleware.get_random_proxy()

        if old_proxy:
            self._proxy_middleware.del_proxy(old_proxy)
        obj = urlparse(new_proxy)
        proxy_args = [
            '--proxy={}'.format(obj.netloc.strip()),
            '--proxy-type={}'.format(obj.scheme),
        ]
        return proxy_args

    def _get_url(self, genre_value, page):
        return self.start_url.format(genre_value=genre_value, page=page)

    def _save_screenshot(self, filename=None):
        if filename is None:
            filename = datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".png"
        self._browser.save_screenshot(filename)
        return filename
