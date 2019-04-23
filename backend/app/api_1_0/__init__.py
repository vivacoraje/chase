from flask import Blueprint

api = Blueprint('api', __name__)

from . import subscription, user, video, auth, search, task, movie, ping, s
