# -*- coding: utf-8 -*-
from lxml import etree
from .search import Ziziyy as _Ziziyy
import requests
import urllib3
import os
from collections import namedtuple
from flask import current_app
from functools import wraps


def pylev_ratio_wrapper(func):
    @wraps(func)
    def wrapper(str1, str2):
        distance = func(str1, str2)
        len1, len2 = len(str1), len(str2)
        ratio = 1 - distance / (len1 + len2)
        return ratio
    return wrapper


try:
    from Levenshtein import ratio as levenshtein_ratio
except ImportError:
    from pylev import levenshtein
    levenshtein_ratio = pylev_ratio_wrapper(levenshtein)

basedir = os.path.abspath(__file__)
fetchdir = os.path.dirname(basedir)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

Rating = namedtuple('rating', ['value', 'count'])


class Handler:

    def __init__(self):
        self.ele_html = None

    def downloader(self, url):
        raise NotImplementedError

    def handler(self):
        raise NotImplementedError

    @property
    def msg(self):
        raise NotImplementedError

    def xpath_like(self, path_like):
        if self.ele_html is None:
            raise ValueError
        if self.ele_html == 0:
            return None
        ele = self.ele_html.xpath(path_like)
        return ele[0] if ele else None


class DoubanSearch(Handler):

    douban_search = 'https://www.douban.com/search?cat=1002&q={}'

    def __init__(self, title):
        self.title = title
        self.douan = None
        super().__init__()

    def downloader(self, url):
        pass

    def handler(self):
        r = requests.get(self.douban_search.format(self.title))
        self.ele_html = etree.HTML(r.text)
        self.douan = self.xpath_like('//*[@id="content"]/div/div[1]/div[3]/div[2]/div[1]/div[2]/div/h3/a/@href')

    @property
    def msg(self):
        return self.douan


class Douban(Handler):

    def __init__(self, url, posters_path=None, poster_origin=False):
        self._url = url
        self.url = None
        self.posters_path = posters_path
        self.poster_origin = poster_origin
        super().__init__()

    def downloader(self, url):
        pass

    def handler(self):
        r = requests.get(self._url)
        self.url = r.url
        self.ele_html = etree.HTML(r.text)

    @property
    def title(self):
        return self.xpath_like('//*[@id="content"]/h1/span[1]/text()')
    
    @property
    def synopsis(self):
        s = self.ele_html.xpath('//*[@id="link-report"]/span/text()')
        return ''.join(_.strip() for _ in s)

    @property
    def poster_path(self):
        poster_url = self.xpath_like('//*[@id="mainpic"]/a/img/@src')
        if self.poster_origin:
            return poster_url
        r = requests.get(poster_url)
        if r.ok:
            poster_folder = self.posters_path or current_app.config['POSTER_FOLDER_PATH']
            if not os.path.exists(poster_folder):
                os.makedirs(poster_folder)
            img_name = poster_url.split('/')[-1]
            img_path = os.path.join(poster_folder, img_name)

            with open(img_path, 'wb') as f:
                f.write(r.content)

            return img_path
        else:
            raise ValueError('Unexpected response')

    @property
    def episode_count(self):
        br = self.ele_html.xpath('//*[@id="info"]/text()')  # [preceding-sibling::br]
        number = None
        for b in br:
            try:
                number = int(b)
                break
            except ValueError:
                pass

        return number

    @property
    def rating(self):
        value = self.xpath_like('//*[@id="interest_sectl"]/div/div[2]/strong/text()')
        count = self.xpath_like('//*[@id="interest_sectl"]/div/div[2]/div/div[2]/a/span/text()')
        return Rating(float(value), int(count))

    @property
    def episode_aired(self):
        return self.xpath_like('//*[@id="info"]/span[@property]/@content')

    @property
    def imdb(self):
        return self.xpath_like('//*[@id="info"]/a[2]/@href')

    @property
    def msg(self):
        return self.imdb


class Imdb(Handler):

    def __init__(self, url):
        self.url = url
        super().__init__()

    def downloader(self, url):
        pass

    def handler(self):
        try:
            r = requests.get(self.url)
        except (requests.ConnectionError, requests.exceptions.MissingSchema):
            self.ele_html = 0
        else:
            self.ele_html = etree.HTML(r.text)

    @property
    def rating(self):
        rvc1 = ('//*[@id="interest_sectl"]/div/div[2]/strong/text()',
                '//*[@id="interest_sectl"]/div/div[2]/div/div[2]/a/span/text()')
        rvc2 = ('//*[@id="title-overview-widget"]/div[1]/div[2]/div/div[1]/div[1]/div[1]/strong/span/text()',
                '//*[@id="title-overview-widget"]/div[1]/div[2]/div/div[1]/div[1]/a/span/text()')
        rvc = rvc1
        value = self.xpath_like(rvc[0])
        if value is None:
            rvc = rvc2
            value = self.xpath_like(rvc[0])
        count = self.xpath_like(rvc[1])
        if count is None:
            count = '0'
        count = count.replace(',', '')
        return Rating(float(value or 0), int(count))

    @property
    def msg(self):
        return None


class Ziziyy(_Ziziyy):

    def __init__(self, title):
        self.url = None
        self.poster_path = None
        super().__init__(title)

    def handler(self):
        r = super().result()
        lower_title = self.title.lower()
        max_ratio_title_index = 0
        max_ratio = 0
        for i, l in enumerate(r):
            ratio = levenshtein_ratio(lower_title, l['title'].lower())
            if ratio > max_ratio:
                max_ratio = ratio
                max_ratio_title_index = i
        self.url = None if max_ratio == 0 else r[max_ratio_title_index]['url']
        self.poster_path = r[max_ratio_title_index]['thumb']


class Movie:

    def __init__(self, title, posters_path=None):
        self.title = title
        self.douban_search = DoubanSearch(title)
        self.douban_search.handler()
        self.douban = Douban(self.douban_search.msg, posters_path=posters_path, poster_origin=True)
        self.douban.handler()
        self.imdb = Imdb(self.douban.msg)
        self.imdb.handler()
        self.ziziyy = Ziziyy(title)
        self.ziziyy.handler()

        self.movie_info = None

    def __iter__(self):
        return iter(self.to_dict().items())

    def fetchable_urls(self):
        if self.movie_info is None:
            self.to_dict()
        urls = []
        for v in self.movie_info['refes'].values():
            if v['fetchable']:
                urls.append(v['url'])
        # [v['url'] for k, v in self.to_dict()['refes'].items() if v['fetchable']]
        return urls

    def to_dict(self):
        self.movie_info = {
            'title': self.douban.title or self.title,
            'synopsis': self.douban.synopsis,
            'poster_path': self.ziziyy.poster_path,
            'episode_aired': self.douban.episode_aired,
            'episode_count': self.douban.episode_count,
            'refes': {
                'douban': {
                    'url': self.douban.url,
                    'rating_value': self.douban.rating.value,
                    'rating_count': self.douban.rating.count,
                    'fetchable': False
                },
                'imdb': {
                    'url': self.imdb.url,
                    'rating_value': self.imdb.rating.value,
                    'rating_count': self.imdb.rating.count,
                    'fetchable': False
                },
                # 'ziziyy': {
                #     'url': self.ziziyy.url,
                #     'fetchable': True
                # }
            },
        }
        return self.movie_info


if __name__ == '__main__':
    mm = Movie('工作细胞')
    from pprint import pprint
    pprint(mm.to_dict())

    mm = {
        'title': 'JOJO的奇妙冒险 黄金之风 ジョジョの奇妙な冒険 黄金の風',
        'episode_aired': '2018-10-06(日本)',
        'episode_count': 39,
        'poster_path': '/Users/everglow/Desktop/py/chase/app/tasks/fetch/posters/p2536255775.jpg',
        'refes': {
            'douban': {
                'rating_count': '5487',
                'rating_value': '9.6',
                'url': 'https://movie.douban.com/subject/27666505/'
            },
            'ziziyy': {
                'url': 'http://www.ziziyy.com/acg/42264/'
            },
            'imdb': {
                'rating_count': '92',
                'rating_value': '9.3',
                'url': 'http://www.imdb.com/title/tt8591978'}
        }
    }
