#coding:utf-8
from __future__ import unicode_literals

from random import randint
from urllib import quote

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
from scrapy.http import Request

from django.db.utils import IntegrityError
from bs4 import BeautifulSoup

from movie_crawler.items.douban import (
    MovieItem, AreaItem, GenreItem, AwardItem,
    TagItem, CelebrityItem, PhotoItem, CommentItem
)


RATING = {
    'allstar50': 5,
    'allstar40': 4,
    'allstar30': 3,
    'allstar20': 2,
    'allstar10': 1,
}


class MovieSpider(CrawlSpider):
    """
        电影爬虫
    """

    name = "douban_movie"
    allowed_domains = ["movie.douban.com", "imdb.com"]
    start_urls = ['http://movie.douban.com/tag/']
    movie_url_extractor = SgmlLinkExtractor(allow=(r'/subject/\d+/'))
    tag_url_extractor = SgmlLinkExtractor(allow=(r'/tag/.+'))
    movie_photo_url_extractor = SgmlLinkExtractor(allow=(r'/photos/photo/\d+/$'))
    celebrity_photo_url_extractor = SgmlLinkExtractor(allow=(r'/celebrity/\d+/photo/\d+/$'))
    celebrity_link = 'http://movie.douban.com/celebrity/%s/'
    celebrity_types = ['stars', 'directors', 'writers']

    def parse(self, response):
        soup = BeautifulSoup(response.body)
        tag_urls = self.tag_url_extractor.extract_links(response)
        return [Request(tag_url.url, callback=self.parse_page) for tag_url in tag_urls]

    def parse_page(self, response):
        soup = BeautifulSoup(response.body)
        try:
            page_num = soup.find('span', attrs={'class': 'thispage'}).attrs['data-total-page']
        except AttributeError:
            page_num = 1
        page_url = response.url + '?start={}'
        return [Request(page_url.format(i * 20), callback=self.parse_movie_urls) for i in range(int(page_num))]

    def parse_movie_urls(self, response):
        movie_urls = self.movie_url_extractor.extract_links(response)
        return [Request(movie_url.url, callback=self.parse_movie_base) for movie_url in movie_urls]

    def parse_movie_base(self, response):
        """
        电影基本信息
        """
        soup = BeautifulSoup(response.body)
        movie = MovieItem()

        # ID
        movie['id'] = int(response.url.split('/')[-2])

        # 标题/年代/评分/简介/上映地区及时间
        movie = self.add_title_etc(soup, movie)

        # 类型
        movie = self.add_genres(soup, movie)

        # 编剧/又名/语言/制片国家地区/官网/IMDB
        movie = self.add_writer_etc(soup, movie)

        # 导演/演员/相关电影
        movie = self.add_director_etc(soup, movie)

        # 标签
        movie = self.add_tags(soup, movie)

        # IMDB 评分
        try:
            id_imdb = movie['id_imdb']
        except KeyError:
            yield movie
        else:
            request = Request('http://www.imdb.com/title/%s/' % movie['id_imdb'], callback=self.parse_rating_imdb)
            request.meta['item'] = movie
            yield request

        cover = self.fillup_movie_cover_image(soup, movie)
        yield cover

        # 获奖
        awards = self.get_movie_awards(soup, movie)
        for award in awards:
            yield award

        # 短评
        short_comments = self.get_short_comments(soup, movie)
        for comment in short_comments:
            yield comment

        # 长评
        review_ids = self.get_review_ids(soup)
        requests = [Request('http://movie.douban.com/review/%s/' % review_id, callback=self.parse_review) for review_id in review_ids]
        for request in requests:
            request.meta['item'] = movie
            yield request

        # 电影剧照
        #yield Request('http://movie.douban.com/subject/%s/photos' % movie['id'], callback=self.parse_movie_photo)

        # 相关艺人详情
        for celebrity_type in self.celebrity_types:
            try:
                movie[celebrity_type]
            except KeyError:
                continue
            else:
                for star in movie[celebrity_type]:
                    yield Request(self.celebrity_link % star['id'], callback=self.parse_celebrity)

    def add_title_etc(self, soup, movie):
        """
        标题/年代/评分/简介/上映地区及时间
        """
        # 标题
        try:
            movie['title'] = soup.find('span', attrs={'property': 'v:itemreviewed'}).text
        except AttributeError:
            pass
        #年代
        try:
            movie['year'] = int(soup.find('span', attrs={'class': 'year'}).text.replace('(', '').replace(')', ''))
        except (AttributeError, ValueError):
            pass
        #评分
        try:
            movie['rating'] = float(soup.find('strong', attrs={'class': 'll rating_num'}).text)
        except (AttributeError, ValueError):
            pass
        #时长
        try:
            movie['runtime'] = soup.find('span', attrs={'property': 'v:runtime'}).attrs['content'].replace(' ', '')
        except AttributeError:
            pass
        #上映日期及地区
        try:
            movie['showing_date'] = [date.attrs['content'] for date in soup.findAll('span', attrs={'property': 'v:initialReleaseDate'})]
        except AttributeError:
            pass
        #简介
        try:
            movie['intro'] = soup.find('span', attrs={'property': 'v:summary'}).text
        except AttributeError:
            pass
        return movie

    def fillup_movie_cover_image(self, soup, movie_item):
        return PhotoItem(
            movie_id=movie_item["id"],
            type="cover",
            url=soup.find('a', attrs={'class': 'nbgnbg'}).find('img').attrs['src']
        )

    def fillup_celebrity_cover_image(self, soup, cele_item):
        return PhotoItem(
            movie_id=cele_item["id"],
            type="cover",
            url=soup.find('a', attrs={'class': 'nbg'}).find('img').attrs['src']
        )

    def add_director_etc(self, soup, movie):
        # 导演
        try:
            director_links = soup.findAll('a', rel='v:directedBy')
        except AttributeError:
            pass
        else:
            director_ids = list(set(self.get_celebrity_ids(director_links)))
            movie['directors'] = [{'id': director_id} for director_id in director_ids]

        # 演员
        try:
            star_links = soup.findAll('a', rel='v:starring')
        except AttributeError:
            pass
        else:
            star_ids = self.get_celebrity_ids(star_links)
            movie['stars'] = [{'id': star_id} for star_id in star_ids]

        # 相关电影
        try:
            relative_links = soup.find(id="recommendations").findAll('a')
        except AttributeError:
            pass
        else:
            relative_ids = list(set(link['href'].split('/')[-2] for link in relative_links))
            movie['relatives'] = [{'id': int(relative_id)} for relative_id in relative_ids]
        return movie

    def add_genres(self, soup, movie):
        try:
            genres = soup.findAll('span', attrs={'property': 'v:genre'})
        except AttributeError:
            pass
        else:
            movie['genres'] = [{'title': genre.text} for genre in genres]
        return movie

    def add_writer_etc(self, soup, movie):
        """
        编剧/又名/语言/制片国家地区/官网/IMDB
        """
        try:
            pl_ele = soup.findAll(attrs={'class': 'pl'})
        except AttributeError:
            pass
        else:
            for pl in pl_ele:
                # 编剧
                if pl.text.startswith('编剧'):
                    writer_links = pl.find_previous('span').findAll('a')
                    writer_ids =  self.get_celebrity_ids(writer_links)
                    movie['writers'] = [{'id': writer_id} for writer_id in writer_ids]
                # 又名
                if pl.text.startswith('又名'):
                    alias = [alias.lstrip() for alias in pl.next_sibling.split('/')]
                    movie['alias'] = alias
                # 语言
                if pl.text.startswith('语言'):
                    language = [lan.replace(' ', '') for lan in pl.next_sibling.split('/')]
                    movie['language'] = language
                # 制片国家/地区
                if pl.text.startswith('制片国家'):
                    areas = pl.next_sibling.split('/')
                    movie['areas'] = [{'name': area} for area in areas]
                # IMDB
                if pl.text.startswith('IMDb链接'):
                    movie['id_imdb'] = pl.next_sibling.next_sibling.text
                # 官网
                if pl.text.startswith('官方网站'):
                    movie['website'] = pl.next_sibling.next_sibling.text
                if pl.text.startswith('季数'):
                    if pl.next_sibling.replace(' ', '').isdigit():
                        movie['season'] = int(pl.next_sibling)
                    if pl.next_sibling.next_sibling.name == 'select':
                        movie['season'] = int(pl.next_sibling.next_sibling.findAll('option')[0].text)
                if pl.text.startswith('集数'):
                    movie['episode'] = int(pl.next_sibling)
                if pl.text.startswith('单集片长'):
                    movie['runtime'] = pl.next_sibling.replace(' ', '')
        return movie

    def add_tags(self, soup, movie):
        try:
            tags = soup.find(attrs={'class': 'tags-body'}).findAll('a')
        except AttributeError:
            pass
        else:
            tags = [tag.text.split('(')[0] for tag in tags]
            movie['tags'] = [{'title': tag} for tag in tags]
        return movie

    def get_short_comments(self, soup, movie):
        # 短评
        try:
            hot_comments = soup.find(id="hot-comments")
            comments_info = hot_comments.findAll(attrs={'class': 'comment-info'})
        except AttributeError:
            return []
        else:
            comment = CommentItem()
            comments = []
            id_comment = [int(cid.attrs['data-cid']) for cid in hot_comments.findAll(attrs={'class': 'comment-item'})]
            votes = [int(vote.text) for vote in hot_comments.findAll(attrs={'class': 'votes pr5'})]
            username = [info.find('a').text for info in comments_info]
            content = [content.text for content in hot_comments.findAll('p', attrs={'class': ''})]
            rating_ele = hot_comments.findAll('span', attrs={'class': 'rating'})
            rating = [RATING[rating.attrs['class'][0]] for rating in rating_ele]
            datetime = [ele.next_sibling.next_sibling.text.replace('\n', '').replace(' ', '') for ele in rating_ele]
            if len(rating) > 0:
                if len(votes) == 0:
                    votes = [0 for i in range(len(rating))]
                for i in range(len(rating)):
                    comment = CommentItem(
                        username=username[i],
                        id_movie = movie['id'],
                        id_comment = id_comment[i],
                        content=content[i],
                        like=votes[i],
                        rating=rating[i],
                        created_time=datetime[i],
                        type=1
                    )
                    comments.append(comment)
            return comments

    def get_review_ids(self, soup):
        # 长评关联
        try:
            review_links = soup.findAll(attrs={'class': 'review-hd-expand'})
        except AttributeError:
            pass
        else:
            review_ids = [link.next_sibling.next_sibling['href'].split('/')[-2] for link in review_links]
            return review_ids

    def get_movie_awards(self, soup, movie):
        try:
            award_ul = soup.findAll(attrs={'class': 'award'})
        except AttributeError:
            pass
        else:
            awards = []
            for ul in award_ul:
                award = AwardItem()
                lis = ul.findAll('li')
                name = lis[0].text.split('届')
                award['name'] = name[-1]
                award['period'] = int(name[0].replace('第', ''))
                award['title'] = lis[1].text
                award['movies'] = [{'id': movie['id']}]
                for li in lis:
                    if li.findAll('a'):
                        star_ids = [star_link['href'].split('/')[-2] for star_link in li.findAll('a')]
                    else:
                        star_ids = None
                if star_ids:
                    award['stars'] = [{'id': int(star_id)} for star_id in star_ids]
                awards.append(award)
            return awards

    def get_celebrity_ids(self, celebrity_links):
        celebrity_ids = []
        for link in celebrity_links:
            celebrity_id = link['href'].split('/')[-2]
            if celebrity_id.isdigit():
                celebrity_ids.append(celebrity_id)
        return celebrity_ids

    def parse_review(self, response):
        soup = BeautifulSoup(response.body)
        id = response.url.split('/')[-2]
        if response.status != 200:
            return
        comment = CommentItem()
        comment['id_comment'] = int(id)
        comment['id_movie'] = response.meta['item']['id']
        try:
            comment['title'] = soup.find('span', attrs={'property': 'v:summary'}).text
        except AttributeError:
            pass
        try:
            comment['content'] = soup.find('div', attrs={'property': 'v:description'}).text
        except AttributeError:
            pass
        try:
            comment['rating'] = RATING[soup.find('span', attrs={'class': 'main-title-rating'}).attrs['class'][0]]
        except AttributeError:
            pass
        comment['username'] = soup.find('span', attrs={'property': 'v:reviewer'}).text
        like = soup.find('em', attrs={'id': 'ucount%su' % id}).text
        comment['like'] = int(like) if like.isdigit() else 0
        dislike = soup.find('em', attrs={'id': 'ucount%sl' % id}).text
        comment['dislike'] = int(dislike) if dislike.isdigit() else 0
        comment['created_time'] = soup.find('span', attrs={'property': 'v:dtreviewed'}).attrs['content']
        comment['type'] = 2
        return comment

    def parse_movie_photo(self, response):
        soup = BeautifulSoup(response.body)
        try:
            page_num = soup.find('span', attrs={'class': 'thispage'}).attrs['data-total-page']
        except:
            page_num = 0
        return [Request(response.url + '?start={}'.format(i*40), callback=self.parse_movie_photo_page) for i in range(int(page_num))]

    def parse_movie_photo_page(self, response):
        photo_urls = list(set(self.movie_photo_url_extractor.extract_links(response)))
        return [Request(url.url, callback=self.parse_movie_photo_base) for url in photo_urls]

    def parse_movie_photo_base(self, response):
        photo = PhotoItem()
        sel = Selector(response)

        photo['url'] = sel.css("div.photo-show img::attr(src)").extract()[0]

        for li in sel.css('ul.poster-info li'):
            title = li.css("::text").extract()[0]
            if title.startswith('电影名称：'):
                photo['movie_id'] = int(li.css("a::attr(href)").extract()[0].split('/')[-2])
            if title.startswith('图片类型'):
                photo['type'] = title.split('：')[-1]
            if title.startswith('原图尺寸'):
                photo['pixel'] = title.split('：')[-1]
            if title.startswith('上传于'):
                photo['upload_time'] = title.replace('上传于', '')
            if title.startswith('文件大小'):
                photo['size'] = title.split('：')[-1]
        yield photo

    def parse_celebrity(self, response):
        soup = BeautifulSoup(response.body)
        celebrity = CelebrityItem()

        # ID
        celebrity['id'] = int(response.url.split('/')[-2])

        celebrity = self.add_celebrity_base(soup, celebrity)
        yield celebrity

        cover = self.fillup_celebrity_cover_image(soup, celebrity)
        yield cover

        awards = self.get_celebrity_awards(soup, celebrity)
        for award in awards:
            yield award

        #yield Request('http://movie.douban.com/celebrity/%s/photos/' % id, callback=self.parse_celebrity_photo)

    def add_celebrity_base(self, soup, celebrity):
        """
        艺人基本信息
        """
        # 姓名
        try:
            celebrity['name'] = soup.find('div', {'id': 'content'}).find('h1').text
        except AttributeError:
            return celebrity
        # 简介
        try:
            celebrity['intro'] = soup.find(attrs={'class': 'short'}).text
        except AttributeError:
            return celebrity
        else:
            for span in soup.find("div", {"id": "headline"}).findAll('li'):
                spans = [span.replace('\n', '').replace(' ', '') for span in span.text.split(':')]
                # 性别
                if spans[0].startswith('性别'):
                    try:
                        celebrity['gender'] = GENDER[spans[1]]
                    except:
                        pass
                # 星座
                if spans[0].startswith('星座'):
                    try:
                        celebrity['constellation']  = spans[1]
                    except:
                        pass
                # 出生日期
                if spans[0].startswith('出生日期'):
                    celebrity['birthday'] = spans[1]
                # 生卒日期
                if spans[0].startswith('生卒日期'):
                    birthday, deathday = spans[1].split('至')
                    celebrity['birthday'] = birthday
                    celebrity['deathday'] = deathday
                    celebrity['isdead'] = True
                # 家庭成员
                if spans[0].startswith('家庭成员'):
                    celebrity['family'] = spans[1].split('/')
                # 职业
                if spans[0].startswith('职业'):
                    celebrity['professions'] = spans[1].split('/')
                # IMDB
                if spans[0].startswith('imdb编号'):
                    celebrity['id_imdb'] = spans[1]
                # 出生地
                if spans[0].startswith('出生地'):
                    celebrity['birthplace'] = spans[1]
                # 官网
                if spans[0].startswith('官方网站'):
                    try:
                        celebrity['website'] = spans[2].replace('//', '')
                    except IndexError:
                        pass
                # 更多中文名
                if spans[0].startswith('更多中文名'):
                    celebrity['alias'] = spans[1].split('/')
                # 更多外文名
                if spans[0].startswith('更多外文名'):
                    celebrity['name_en'] = spans[1].split('/')
            return celebrity

    def get_celebrity_awards(self, soup, celebrity):
        """
        获奖情况
        """
        try:
            award_ul = soup.findAll(attrs={'class': 'award'})
        except AttributeError:
            pass
        else:
            awards = []
            for ul in award_ul:
                award = AwardItem()
                lis = ul.findAll('li')
                name = lis[1].text.split('届')
                award['name'] = name[-1]
                award['period'] = int(name[0].replace('第', ''))
                award['year'] = lis[0].text.replace('年', '')
                award['title'] = lis[2].text
                award['stars'] = [{'id': celebrity['id']}]
                for li in lis:
                    if li.findAll('a'):
                        movie_ids = [movie_link['href'].split('/')[-2] for movie_link in li.findAll('a')]
                        award['movies'] = [{'id': movie_id} for movie_id in movie_ids]
                awards.append(award)
            return awards

    def parse_celebrity_photo(self, response):
        soup = BeautifulSoup(response.body)
        try:
            page_num = soup.find('span', attrs={'class': 'thispage'}).attrs['data-total-page']
        except:
            page_num = 0
        return [Request(response.url + '?start={}'.format(i*40), callback=self.parse_celebrity_photo_page) for i in range(int(page_num))]

    def parse_celebrity_photo_page(self, response):
        photo_urls = list(set(self.celebrity_photo_url_extractor.extract_links(response)))
        return [Request(url.url, callback=self.parse_celebrity_photo_base) for url in photo_urls]

    def parse_celebrity_photo_base(self, response):
        photo = PhotoItem()
        soup = BeautifulSoup(response.body)
        try:
            info_li = soup.find('ul', attrs={'class': 'poster-info'}).findAll('li')
        except AttributeError:
            return

        photo['celebrity_id'] = int(response.url.split('/')[-4])
        photo['url'] = soup.find('div', attrs={'class': 'photo-show'}).find('img')['src']
        for li in info_li:
            if li.text.startswith('原图尺寸'):
                photo['pixel'] = li.text.split('：')[-1]
            if li.text.startswith('上传于'):
                photo['upload_time'] = li.text.replace('上传于', '')
            if li.text.startswith('文件大小'):
                photo['size'] = li.text.split('：')[-1]
        yield photo

    def parse_rating_imdb(self, response):
        movie = response.meta['item']
        soup = BeautifulSoup(response.body)
        try:
            rating_imdb = soup.find('div', attrs={'class': 'titlePageSprite star-box-giga-star'}).text
        except AttributeError:
            yield movie
        else:
            movie['rating_imdb'] = rating_imdb
            yield movie
