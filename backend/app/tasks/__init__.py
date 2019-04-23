# -*- coding: utf-8 -*-
from app import create_app, celery
import os

config_name = os.environ.get('KURA_CONFIG')
app = create_app()
app.app_context().push()
celery = celery
