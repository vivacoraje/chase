# -*- coding: utf-8 -*-

from .test_client import TestClient


class UserTestCase(TestClient):

    def test_user(self):
        r, s, h = self.get('/api/users')
        self.assertEqual(s, 200)
        user = {
            "email": "test@test.com",
            "password": "123456",
            "username": "test"
        }
        r, s, h = self.post('/api/users', data=user)
        self.assertEqual(s, 201)
        self.assertEqual(h['Location'], 'http://localhost/api/users/test')

        r, s, h = self.post('/api/users', data=user)
        self.assertEqual(s, 202)

        r, s, h = self.get('/api/users/'+user['username'])
        self.assertEqual(s, 200)

        r, s, h = self.get('/api/users/faker')
        self.assertEqual(s, 404)

        r, s, h = self.post('/api/tokens', basic_auth='test@test.com:123456')
        self.assertEqual(s, 200)

        r, s, h = self.delete('/api/users/'+user['username'], basic_auth='test@test.com:123456')
        self.assertEqual(s, 200)
