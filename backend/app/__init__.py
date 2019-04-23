# -*- coding: utf-8 -*-
from flask import Flask
from .extensions import db, api, mail, cors, admin
from config import config
from celery import Celery
import os
from flask_admin.contrib.sqla import ModelView
from .models import User, Subscription, Movie, UserVideo, FetchRecord, \
    Search, Video, Refe, Fetcher

_config = config[os.environ.get('CHASE_CONFIG', 'development')]
celery = Celery(__name__, broker=_config.CELERY_CONFIG['CELERY_BROKER_URL'])


admin.add_views(
    ModelView(User, session=db.session),
    ModelView(UserVideo, session=db.session),
    ModelView(Movie, session=db.session),
    ModelView(Subscription, session=db.session),
    ModelView(Video, session=db.session),
    ModelView(Search, session=db.session),
    ModelView(FetchRecord, session=db.session),
    ModelView(Refe, session=db.session),
    ModelView(Fetcher, session=db.session)
)


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('CHASE_CONFIG', 'development')
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

    celery.conf.update(**app.config['CELERY_CONFIG'])

    # 之后的蓝图需用到db 而db必须要有应用上下文 故而先要对db进行依赖注入
    db.init_app(app)

    mail.init_app(app)
    cors.init_app(app)
    admin.init_app(app)
    cors.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .api_1_0 import api as api_1_0_blueprint
    # 这里给url_prxfix值也不会生效， 会被restful.Api.add_resource中的url_prefix覆盖
    app.register_blueprint(api_1_0_blueprint)
    # 在蓝图注册之后 蓝图中的restful.api实例才能生效
    api.init_app(app)

    return app
