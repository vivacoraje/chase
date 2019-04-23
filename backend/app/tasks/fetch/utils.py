import base64
from queue import Queue
from threading import Thread
import requests


def thunder_to_magnet(url):
    tail = url.split('thunder://')[-1]
    temp = base64.b64decode(tail.encode())
    temp = temp[2:-2]
    return temp.decode()


def magent_to_thunder(url):
    temp = ''.join(['AA', url, 'ZZ'])
    return 'thunder://' + base64.b64encode(temp.encode()).decode('utf-8')


def fetcher(url, queue):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
    }
    try:
        r = requests.get(url, timeout=10, headers=headers)
    except:
        r = None
    queue.put(r)


def return_early(urls, queue):
    for u in urls:
        t = Thread(target=fetcher, args=(u, queue))
        t.start()
    while not queue.full():
        pass


class ReturnEarly:

    def __init__(self, args):
        self._queue = Queue(maxsize=1)
        super().__init__(args=args)
        self.r = None

    def _checker(self):
        while not self._queue.full():
            pass
        return

    def _fetcher(self, urls):
        try:
            r = requests.get(self._args[0], timeout=10)
        except:
            r = None
        self._queue.put(r)
        self._checker()


if __name__ == '__main__':
    print(magent_to_thunder('magnet:?xt=urn:btih:7Z2KSNLG7QZXBDXX6YBIYGYTCFZGRKPH'))
    urls = ['https:/baidu.com', 'https://bing.cn']
    q = Queue(maxsize=1)
    return_early(urls, q)
    r = q.get()
    if r:
        print(r.url)
    else:
        print('nothing fetched')
