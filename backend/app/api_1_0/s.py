from . import api
from flask import jsonify


@api.route('/api/s', methods=['GET'])
def apis():
    return jsonify([
      '/api/movies',
      '/api/movies/<id>',
      '/api/ping',
      '/api/search',
      '/api/search/recently',
      '/api/search/stats',
      '/api/subscriptions',
      '/api/subscriptions/<username>',
      '/api/subscriptions/<username>/<sub_id>',
      '/api/tasks',
      '/api/tasks/<path:task_name>',
      '/api/tokens',
      '/api/users',
      '/api/users/<username>',
      '/api/videos/<username>/<video_id>',
      '/api/videos/<username>/subs/<subs_id>'
    ])