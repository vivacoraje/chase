# -*- coding: utf-8 -*-
from flask_restful import Resource
from ..extensions import api
from celery.beat import Scheduler
from .. import celery
import redis
import sys
import jsonpickle
from ..schedule import scheduler


class TasksApi(Resource):

    def get(self):
        d = []
        tasks = scheduler.rdb.zrange(scheduler.key, 0, -1) or []
        for t in tasks:
            cl = jsonpickle.decode(t)
            task = {
                'args': cl.args,
                'task': cl.task,
                'schedule': str(cl.schedule),
                'name': cl.name,
                'last_run_at': str(cl.last_run_at),
                'total_run_count': cl.total_run_count
            }
            d.append(task)
        return d


api.add_resource(TasksApi, '/api/tasks')


class TaskApi(Resource):

    def get(self, task_name):
        task_obj = None
        for task in scheduler.tasks:
            task = jsonpickle.loads(task)
            if task.name == task_name:
                task_obj = task
                break
        return {
            'args': task_obj.args,
            'task': task_obj.task,
            'schedule': str(task_obj.schedule.day_of_week),
            'name': task_obj.name,
            'last_run_at': str(task_obj.last_run_at),
            'total_run_count': task_obj.total_run_count
        } if task_obj else ('Not found', 404)

    def post(self, task_name):
        from app.utils import init_schedule
        scheduler.add(**{
            'name': task_name,
            'task': 'app.tasks.tasks.crawler_task',
            'schedule': init_schedule(),
            'args': (task_name,)
        })
        return 'ok'

    def delete(self, task_name):
        scheduler.remove(task_name)


api.add_resource(TaskApi, '/api/tasks/<path:task_name>')
from datetime import timedelta

class TestTaskApi(Resource):

    def get(self):
        from app.tasks.tasks import test
        test.delay()

    def post(self):
        scheduler.add(**{
            'name': 'celery:beat:task:https://koyimusic.ctfile.com/fs/2676556-292033986',
            'task': 'app.tasks.tasks.test',
            'schedule': timedelta(10),
            'args': ('')
        })

    def put(self):
        scheduler.replace('celery:beat:task:test', timedelta(30))

    def delete(self):
        scheduler.remove('celery:beat:task:test')


api.add_resource(TestTaskApi, '/api/tasks/test')
