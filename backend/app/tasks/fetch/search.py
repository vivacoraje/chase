# -*- coding: utf-8 -*-
import requests
from requests.adapters import HTTPAdapter
from lxml import etree
from abc import ABCMeta, abstractmethod
import asyncio
import time
from urllib.parse import urlparse
from threading import Thread


class Search(metaclass=ABCMeta):

    def __init__(self, title):
        self.title = title
        self.session = self.__session()

    @staticmethod
    def __session():
        s = requests.Session()
        s.mount('http://', HTTPAdapter(max_retries=3))
        s.mount('https://', HTTPAdapter(max_retries=3))
        return s

    @abstractmethod
    def result(self):
        pass

    def __str__(self):
        return self.__class__.__name__.lower()


class Loldytt(Search):
    disable = object()

    def __init__(self, title):
        self.search_url = 'https://{}.loldytt.tv/search/index.asp'  # 'www', 'm'
        super().__init__(title)

    def result(self, queue=None):
        data = {'keyword': self.title.encode('gbk')}
        www_or_m = None
        try:
            www_or_m = 'www'
            r = self.session.post(
                                self.search_url.format(www_or_m),
                                data=data,
                                timeout=3)
            r.encoding = 'gbk'
        except requests.exceptions.ConnectionError:
            www_or_m = 'm'
            r = self.session.post(
                                self.search_url.format(www_or_m),
                                data=data,
                                timeout=3)
            r.encoding = 'gbk'
        except:
            if queue:
                queue.put(None)
            return

        ele_html = etree.HTML(r.text)
        titles = ele_html.xpath('/html/body/center/div[5]/ol/label/a/text()')
        urls = ele_html.xpath('/html/body/center/div[5]/ol/label/a/@href')

        if www_or_m == 'm':
            urls = [self.replce(u, 'www', 'm') for u in urls]
        urls = [self.replce(u, 'www.dytt789.com', 'www.loldytt.tv') for u in urls]
        res = [{'title': t, 'url': u} for t, u in zip(titles, urls)]
        if queue:
            queue.put(res)
        else:
            return res

    def replce(self, url, src, dst):
        """
        replace('https://www.*.com/', 'www', 'm') => 'https://m.*.com/'
        replace('https://www.*.com/', 'com', 'tv') => 'https://www.*.tv/'
        """
        parse_result = urlparse(url)
        netloc_to_m = parse_result.netloc.replace(src, dst)
        return parse_result.scheme + '://' + netloc_to_m + parse_result.path


class Loldyttw(Search):
    disable = object()

    def __init__(self, title):
        self.search_url = 'http://www.loldyttw.net/e/search/index.php'
        super().__init__(title)

    def result(self, queue=None):
        data = {
            'keyboard': self.title.encode('gbk'),
            'show': 'title,newstext',
            'tbname': 'download',
            'tempid': '1',
            'submit': b'\xef\xbf\xbd\xef\xbf\xbd\xef\xbf\xbd\xef\xbf\xbd\xd2\xbb\xef\xbf\xbd\xef\xbf\xbd'
        }
        try:
            r = self.session.post(self.search_url, data=data)
        except:
            if queue:
                queue.put(None)
            return

        ele_html = etree.HTML(r.text)
        titles = ele_html.xpath('/html/body/center/div[6]/ol/label/a/text()')
        urls = ele_html.xpath('/html/body/center/div[6]/ol/label/a/@href')
        res = [{'title': t, 'url': 'http://www.loldyttw.net'+u} for t, u in zip(titles, urls)]
        if queue:
            queue.put(res)
        else:
            return res


class Ziziyy(Search):

    def __init__(self, title):
        self.search_url = 'http://v.mtyee.com/ssszz.php?top=10&q=' + title
        super().__init__(title)

    def result(self, queue=None):
        headers = {'Origin': 'http://www.ziziyy.com/search.php'}
        r = self.session.get(self.search_url, headers=headers)
        r.encoding = 'utf-8-sig'
        res = r.json()
        if queue:
            queue.put(res)
        else:
            return res


class Download:

    def __init__(self):
        pass

    async def downloader(self, der):
        r = der.result()
        return r

    def run(self, ders):
        start = time.time()
        tasks = [asyncio.ensure_future(self.downloader(ders[0])), asyncio.ensure_future(self.downloader(ders[1]))]
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))
        end = time.time()
        print("fetch from '{}', '{}'...\ntime: {}".format(ders[0].search_url, ders[1].search_url, end-start))
        return tasks


def search(title):
    results = {}
    for c in Search.__subclasses__():
        if hasattr(c, 'disable'):
            continue
        r = c(title)
        results.update({
            str(r): r.result()
        })
    return results


def asycnc_search(title, queue):
    for c in Search.__subclasses__():
        if hasattr(c, 'disable'):
            continue
        r = c(title)
        t = Thread(target=r.result, args=(queue,))
        t.start()


if __name__ == '__main__':
    from pprint import pprint
    jojo = search('jojo')
    pprint(jojo)
