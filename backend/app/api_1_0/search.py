# -*- coding: utf-8 -*-
from ..models import User, Search, Subscription
from ..extensions import api, db
from flask_restful import Resource, reqparse, fields, marshal
from flask import request
from app.tasks.fetch.search import search


ziziyy_fields = {
    'title': fields.String,
    'url': fields.String
}


class SearchApi(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', required=True)
        self.reqparse.add_argument('email')
        super().__init__()

    def post(self):
        args = self.reqparse.parse_args()
        title, email = args['title'], args['email']
        titles = []
        if email:
            user = User.query.filter_by(email=email).first()
            if user:
                subscriptions = user.subscriptions.filter(Subscription.title.ilike('%'+title+'%')).all()
                titles = [s.title for s in subscriptions]

        sch = Search(keywords=title)
        r = search(title)
        if r or titles:
            sch.hit = True
        db.session.add(sch)
        db.session.commit()
        
        # for t in titles:
        #     for i, kv in enumerate(r['loldytt']):
        #         if kv['title'] == t:
        #             r['loldytt'].pop(i)
        # d = {
        #     'subs': titles,
        #     'non': r['loldytt'],
        #     'online': marshal(r['ziziyy'], ziziyy_fields)
        # }
        for t in titles:
            for i, kv in enumerate(r['ziziyy']):
                if kv['title'] == t:
                    r['ziziyy'].pop(i)
        d = {
            'subs': titles,
            'non': marshal(r['ziziyy'], ziziyy_fields),
        }
        return d


api.add_resource(SearchApi, '/api/search')


class SearchRecentlyApi(Resource):

    def get(self):
        args = request.args.get('limit', 10)
        search = Search.query.order_by('timestamp').all()[-int(args):]
        search.reverse()

        return [s.to_dict() for s in search]


api.add_resource(SearchRecentlyApi, '/api/search/recently')


class SearchStatsApi(Resource):

    def get(self):
        s = Search.query.all()
        d = {}
        for i in s:
            if i.keywords not in d:
                d[i.keywords] = {}
                d[i.keywords]['count'] = 0
                d[i.keywords]['at_last'] = 0
            d[i.keywords]['count'] += 1

            d[i.keywords]['at_last'] = i.timestamp if i.timestamp > d[i.keywords]['at_last'] else d[i.keywords]['at_last']
        return d


api.add_resource(SearchStatsApi, '/api/search/stats')
