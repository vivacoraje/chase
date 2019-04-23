# -*- coding: utf-8 -*-
from ..extensions import api, db, token_auth
from app.models import Subscription, User, Movie, Fetcher
from flask_restful import Resource, reqparse
from app.tasks.tasks import fetch_movie_info, fetch_chain


class SubscribeApi(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('tv_url', required=True, type=str)
        # self.reqparse.add_argument('token')
        super().__init__()

    def get(self, username):
        user = User.query.filter_by(username=username).first()
        if user:
            subs = user.subscriptions
            return [sub.to_dict(username=username, include_poster=True, include_title=True) for sub in subs]
        return {'message': "user invalid"}, 404

    @token_auth.login_required
    def post(self, username):
        user = User.query.filter_by(username=username).first()
        if user is None:
            return {'message': 'username invalid'}, 404
        if not user.confirmed:
            return {'message': 'please activate your account'}, 403
        tv_url = self.reqparse.parse_args()['tv_url']

        fetcher = Fetcher.query.filter_by(url=tv_url).first()

        # 订阅不存在
        if fetcher is None:
            movie = Movie()
            subscription = Subscription()
            subscription.add_one_user()
            user.subscriptions.append(subscription)
            movie.subscription = subscription
            db.session.add(movie)
            db.session.commit()
            fetch_chain(movie.id, tv_url)

            return {'id': subscription.id, 'url': tv_url}, 201

        subscription = fetcher.subscription
        # 订阅存在
        # 但当前用户未订阅
        if not user.subscriptions.filter_by(id=subscription.id).first():
            subscription.add_one_user()
            subscription.users.append(user)
            user.subscriptions.append(subscription)
            for fetcher in subscription.fetchers:
                for video in fetcher.videos:
                    user.add_video(video=video, fetcher=fetcher)
            db.session.commit()
        # 用户已订阅

        return subscription.to_dict(username=username), 201


api.add_resource(SubscribeApi, '/api/subscriptions/<username>')


class SubscriptionApi(Resource):

    def get(self, username, sub_id):
        user = User.query.filter_by(username=username).first()
        if user:
            sub_s = user.subscriptions.filter_by(id=sub_id).first()  
            if sub_s:
                return sub_s.to_dict(username=username)
            return {'message': '@{} not subscribed sub_id#{}'.format(username, sub_id)}, 404
        return {'message': 'user invalid'}, 404

    def delete(self, username, sub_id):
        user = User.query.filter_by(username=username).first()
        s = user.subscriptions.filter_by(id=sub_id).delete()
        return {'message': 'deleted'}


api.add_resource(SubscriptionApi, '/api/subscriptions/<username>/<sub_id>')


class SubscriptionsApi(Resource):

    def get(self):
        subs = Subscription.query.all()
        return [sub.to_dict(include_poster=True) for sub in subs]


api.add_resource(SubscriptionsApi, '/api/subscriptions')
