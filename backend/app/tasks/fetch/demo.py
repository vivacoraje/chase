from queue import Queue
from threading import Thread
import time
import requests


def producter(out_q, urls):
    for u in urls:
        out_q.put(u)

def consumer(in_q):
    while True:
        url = in_q.get()
        r = requests.get(url)
        