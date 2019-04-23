# -*- coding: utf-8 -*-
import unittest
import json
from app import create_app, db
from .test_client import TestClient


class SubscriptionTestCase(TestClient):

    def test_user(self):
        r, s, h = self.get('/api/users')
        self.assertEqual(s, 200)

        r, s, h = self.post('/api/users',
                            data={
                                'email': 'example@email.com',
                                'password': '123456',
                                'username': 'example'
                            })
        self.assertEqual(s, 201)

    def test_get_all_subscritpions(self):
        r, s, h = self.get('/api/subscriptions')
        self.assertEqual(s, 200)

    def test_get_subscripttion(self):
        r, s, h = self.get('/api/subscriptions/test_user')
        self.assertEqual(s, 404)

        sub = {'tv_url': 'http://test.tv'}
        r, s, h = self.post('/api/subscriptions/test_user', data=sub)
        self.assertEqual(s, 404)

        user = {'email': 'example@email.com', 'password': '123456', 'username': 'test_user'}
        self.post('/api/users', data=user)

        r, s, h = self.post('/api/subscriptions/test_user', data=sub)
        self.assertEqual(s, 201)


if __name__ == '__main__':
    unittest.main()
