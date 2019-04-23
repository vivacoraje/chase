# -*- coding: utf-8 -*-
from app.tasks.fetch import search
import unittest


class TasksTestCase(unittest.TestCase):

    def test_search(self):
        task = search('jojo')
        self.assertEqual(len(task), 7)
