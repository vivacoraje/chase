# -*- coding: utf-8 -*-
from collections import defaultdict
from math import sqrt
from celery.schedules import crontab
import time
from urllib.parse import urlparse
from datetime import datetime
from numbers import Number
from collections import Callable
import random


def timestamp():
    return int(time.time())


def weekday(time_stamp):
    stamp = None
    if isinstance(time_stamp, Number):
        stamp = time_stamp
    elif isinstance(time_stamp, Callable):
        stamp = time_stamp()
    return datetime.fromtimestamp(stamp).weekday()


def domain(url):
    return urlparse(url).netloc.split('.')[1]


def trending_search(kw):
    words = defaultdict(int)
    prev = None
    for k in kw:
        words[k] += 1
        if prev is not None:
            words['%s %s' % (prev, k)] += 1
            words[prev] -= 1
            words[k] -= 1
        prev = k
    trending = sorted(words.items(), key=lambda o: o[1], reverse=True)[:15]
    return trending


class Fazscore:
    def __init__(self, decay, pop=[]):
        self.sqrAvg = self.avg = 0
        # The rate at which the historic data's effect will diminish.
        self.decay = decay
        for x in pop:
            self.update(x)

    def update(self, value):
        # Set initial averages to the first value in the sequence.
        if self.avg == 0 and self.sqrAvg == 0:
            self.avg = float(value)
            self.sqrAvg = float((value ** 2))
        # Calculate the average of the rest of the values using a
        # floating average.
        else:
            self.avg = self.avg * self.decay + value * (1 - self.decay)
            self.sqrAvg = self.sqrAvg * self.decay + (value ** 2) * (1 - self.decay)
        return self

    def std(self):
        # Somewhat ad-hoc standard deviation calculation.
        return sqrt(self.sqrAvg - self.avg ** 2)

    def score(self, obs):
        if self.std() == 0:
            return (obs - self.avg) * float("infinity")
        else:
            return (obs - self.avg) / self.std()


def make_pair(l1, l2):
    pairs = []
    if len(l1) > len(l2):
        long, short = l1, l2
    else:
        long, short = l2, l1
    for l in long:
        max_ratio = 0
        max_title = None
        for s in short:
            ratio = Levenshtein.ratio(l, s)
            if ratio > max_ratio:
                max_ratio = ratio
                max_title = s
        pairs.append((l, max_title, max_ratio))
    return pairs


def init_schedule():
    return crontab(minute=random.randint(0, 59), hour=random.randint(0, 23))
