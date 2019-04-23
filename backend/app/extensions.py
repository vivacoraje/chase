from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_mail import Mail
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth
from flask_cors import CORS
from flask_admin import Admin, BaseView, expose


db = SQLAlchemy()
api = Api()
mail = Mail()
basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth(scheme='Bearer')
multi_auth = MultiAuth(basic_auth, token_auth)
cors = CORS()
admin = Admin(name='Kura', template_mode='bootstrap3')
