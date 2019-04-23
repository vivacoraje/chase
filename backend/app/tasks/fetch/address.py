# -*- coding: utf-8 -*-
import requests
from collections import namedtuple
from pyquery import PyQuery
from lxml import etree
from urllib.parse import urlparse

PROXIES = []
REFERER = []


Episode = namedtuple('Episode', ['title', 'address'])
# address_type: `downloadable`, `playable'`
Item = namedtuple('Item', ['url', 'title', 'episodes', 'address_type'])

DOWNLOADABLE, PLAYABLE = ('downloadable', 'playable')


class Fetch:

    def __init__(self, url):
        self.url = url
        self.title = None
        self.html = None
        self.episodes = None
        self.encode = None
        self.address_type = None

    def extractor(self):
        pass

    def download(self):
        try:
            res = requests.get(self.url)
        except:
            return None
        if res:
            if self.encode:
                res.encoding = self.encode
            self.html = res.text
            return True

    def run(self):
        if self.download() is None:
            return None
        self.extractor()
        return Item(url=self.url, title=self.title, episodes=self.episodes, address_type=self.address_type)


class Dytt789(Fetch):

    def __init__(self, url):
        super().__init__(url)
        self.encode = 'gbk'
        self.address_type = DOWNLOADABLE

    def extractor(self):
        doc = PyQuery(self.html)
        self.title = doc('h1')('a').text()
        ul1li = doc('ul#ul1')('li')('a').items()
        self.episodes = [Episode(title=_.attr('title'), address=_.attr('href')) for _ in ul1li]


Dytt789.__name__ = 'Loldytt'


class Dytt789m(Fetch):

    def __init__(self, url):
        super().__init__(url)
        self.encode = 'gbk'
        self.address_type = DOWNLOADABLE

    def extractor(self):
        doc = etree(self.html)
        self.title = doc.xpath('//*[@id="sec_info"]/h2/text()[3]')[0].split(' ')[-1]
        titls = doc.xpath('/html/body/section/div[2]/div/ul/li/a/text()')
        address = doc.xpath('/html/body/section/div[2]/div/ul/li/a/@href')
        self.episodes = [Episode(title=t, address=a) for t, a in zip(titls, address)]


class Loldyttw(Fetch):

    def __init__(self, url):
        super().__init__(url)
        self.encode = 'gbk'
        self.address_type = DOWNLOADABLE

    def extractor(self):
        doc = PyQuery(self.html)
        self.title = doc('h1')('a').text()
        ul1li = doc('ul#ul1')('li')('a').items()
        self.episodes = [Episode(title=_.attr('title'), address=_.attr('href')) for _ in ul1li]


class Ziziyy(Fetch):

    def __init__(self, url):
        super().__init__(url)
        self.encode = 'utf-8'
        self.address_type = PLAYABLE

    def extractor(self):
        doc = etree.HTML(self.html)
        self.title = doc.xpath('/html/body/div[2]/div[2]/div[2]/dl/dt[1]/text()')[0]
        play_address = doc.xpath('//*[@id="stab_1_71"]/ul/li/a/@href')
        titles = doc.xpath('//*[@id="stab_1_71"]/ul/li/a/text()')
        self.episodes = [Episode(title=t, address=a) for t, a in zip(titles, play_address)]


class Fjisu(Fetch):

    def __init__(self, url):
        super().__init__(url)
        self.encode = 'utf-8-sig'
        self.address_type = PLAYABLE

    def extractor(self):
        doc = etree.HTML(self.html)
        self.title = doc.xpath('/html/body/div[3]/div/div/div/div[2]/div[1]/div[1]/div/h1/text()')[0]
        play_address = doc.xpath('//*[@id="qiyi-pl-list"]/div/ul/li/a/@href')
        titles = doc.xpath('//*[@id="qiyi-pl-list"]/div/ul/li/a/@title')
        self.episodes = [Episode(title=t, address=self.url+a) for t, a in zip(titles, play_address)]


class AddressFetcher:

    def __init__(self):
        self.subclass = {F.__name__: F for F in Fetch.__subclasses__()}
        self.ok = None

    @staticmethod
    def domain(url):
        netloc = urlparse(url).netloc.split('.')
        netloc_len = len(netloc)
        if netloc_len == 2:
            domain = netloc[0]
        elif netloc_len == 3:
            domain = netloc[1]
        else:
            raise ValueError("could't found domain")
        return domain

    def fetch(self, url):
        """
        return: `Item`
        """
        domain_cap = self.domain(url).capitalize()
        f = self.subclass[domain_cap](url)
        return f.run()


if __name__ == '__main__':
    fetcher = AddressFetcher()
    print(fetcher.subclass)
    fetcher.fetch('https://www.dytt789.tv/Zuixinriju/UNNATURAL/')
    # f1 = fetcher.fetch('http://www.ziziyy.com/search.php/tv/17127/')
    # print(f1)
    # f2 = fetcher.fetch('https://www.dytt789.com/Zuixinriju/UNNATURAL/')
    # print(f2)
    # f3 = fetcher.fetch('http://fjisu.com/acg/1904/')
    # print(f3)
    # f4 = fetcher.fetch('http://www.loldyttw.net/Dongman/26472.html')
    # print(f4)
