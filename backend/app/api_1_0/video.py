# -*- coding: utf-8 -*-
from ..models import Video, User, Subscription, UserVideo
from ..extensions import api, multi_auth, token_auth
from flask_restful import Resource


class VideosApi(Resource):

    def get(self, username, subs_id):
        user = User.query.filter_by(username=username).first()
        subs = Subscription.query.filter_by(id=subs_id).first()
        if user is None or subs is None:
            return 'subscription #{} invalid for @{}'.format(subs_id, username), 404
        videos = user.user_subs_videos(subs)
        if videos:
            return {
                'title': subs.movie.title,
                'videos': videos
            }
        return 'user invalid', 404


api.add_resource(VideosApi, '/api/videos/<username>/subs/<subs_id>')


class VideoApi(Resource):

    def get(self, username, video_id):
        user = User.query.filter_by(username=username).first()
        if user:
            uv = user.videos.filter_by(video_id=video_id).first()
            if uv:
                return uv.video_to_dict()

    @token_auth.login_required
    def put(self, username, video_id):
        user = User.query.filter_by(username=username).first()
        if user:
            uv = UserVideo.query.filter_by(user_id=user.id, video_id=video_id).first()
            if uv:
                uv.switch_finished()
                return uv.video_to_dict()
            return {'message': 'video id invalid'}, 404
        return {'message': 'user does not exist'}, 404


api.add_resource(VideoApi, '/api/videos/<username>/<video_id>')
