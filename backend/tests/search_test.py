# -*- coding: utf-8 -*-
from .test_client import TestClient


class SearchTestCase(TestClient):

    def test_search(self):
        r, s, h = self.post('/api/search', data={'title': 'jojo'})
        self.assertEqual(s, 200)

    def test_search_recently(self):
        r, s, h = self.get('/api/search/recently')
        self.assertEqual(s, 200)
