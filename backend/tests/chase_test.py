# -*- coding: utf-8 -*-
from app import create_app, db
import unittest


class ChaseTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')

