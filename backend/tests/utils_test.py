# -*- coding: utf-8 -*-
import unittest
from app.utils import weekday, timestamp


class UtilsTestCase(unittest.TestCase):

    def test_utils(self):
        _timestamp = 1550673852
        _weekday = weekday(_timestamp)
        self.assertEqual(_weekday, 2)

        self.assertEqual(_weekday, weekday(timestamp))
