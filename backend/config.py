import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:

    #: app
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or "top secret."

    #: DB
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://chase:123456@localhost:3306/chase'

    PER_PAGE = 10

    #: Mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 567)
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SUBJECT_PREFIX = '[chase]'
    MAIL_SENDER = 'Chase Admin <{}>'.format(MAIL_USERNAME)

    # poster
    POSTER_FOLDER_PATH = os.environ.get('POSTER_FOLDER_PATH') or os.path.join(basedir, 'app/static/posters')

    #: Celery
    CELERY_CONFIG = {}

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    CELERY_CONFIG = {
        'CELERY_BROKER_URL': os.environ.get('CELERY_BROKER_URL'),
        'CELERY_RESULT_BACKEND': os.environ.get('CELERY_RESULT_BACKEND'),
        'CELERY_TASK_SERIALIZER': 'json',
        'CELERY_REDIS_SCHEDULER_URL': os.environ.get('CELERY_REDIS_SCHEDULER_URL')
    }


class ProductionConfig(Config):
    pass


class Testing:
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///./test.db'


config = {
    'default': Config,
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': Testing
}
