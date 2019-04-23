from . import api
from flask import jsonify


@api.route('/api/ping')
def ping():
    return jsonify({'msg': 'pong!'})
