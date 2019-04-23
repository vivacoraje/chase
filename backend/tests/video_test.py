# -*- coding: utf-8 -*-
from app.models import Video
from .test_client import TestClient


class VideoTestCase(TestClient):
    def test_get(self):
        r, s, h = self.get('api/videos/')
