# -*- coding: utf-8 -*-
from app import celery
from .scheduler import MyRedisScheduler

# (°ー°〃)
scheduler = MyRedisScheduler(app=celery)
