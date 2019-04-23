# -*- coding: utf-8 -*-
from celery.schedules import maybe_schedule
from .celerybeatredis.redisbeat import RedisScheduler
import jsonpickle


class MyRedisScheduler(RedisScheduler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def tasks(self):
        return self.rdb.zrange(self.key, 0, -1) or []

    def add_entry(self, e):
        self.rdb.zadd(self.key, {self._when(e, e.is_due()[1]) or 0: jsonpickle.encode(e)})
        return True

    def replace(self, task_name, schedule):
        tasks = self.rdb.zrange(self.key, 0, -1) or []
        for idx, task in enumerate(tasks):
            entry = jsonpickle.decode(task)
            if entry.name == task_name:
                self.rdb.zremrangebyrank(self.key, idx, idx)
                entry.schedule = maybe_schedule(schedule)
                return self.add_entry(entry)
        else:
            return False

    def get_schedule(self, task_name):
        tasks = self.rdb.zrange(self.key, 0, -1) or []
        for idx, task in enumerate(tasks):
            entry = jsonpickle.decode(task)
            if entry.name == task_name:
                return entry.schedule
