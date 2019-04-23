# -*- coding: utf-8 -*-
from ..extensions import db, api, multi_auth, basic_auth
from ..models import User
from flask_restful import Resource, reqparse
from flask import make_response, jsonify, url_for, render_template
from sqlalchemy import or_
from ..tasks.send_email import send_email


class UsersApi(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('email', type=str, required=True)
        self.reqparse.add_argument('password', type=str, required=True)
        self.reqparse.add_argument('username', type=str, required=True)
        super().__init__()

    def get(self):
        """
        获取所有用户
        :return:
        """
        users = User.query.all()

        return [user.to_dict() for user in users]

    def post(self):
        """
        创建新用户
        :return:
        """
        args = self.reqparse.parse_args()

        _user = User.query.filter(
            or_(User.email == args['email'], User.username == args['username'])
        ).first()

        user = User.create(args)

        if _user is not None:
            if _user.confirmed:
                return {'message': 'email or username already exists'}, 202
            else:
                user = _user

        confirm_token = user.generate_confirmation_token()
        send_email.delay(user.email,
                         '激活账户',
                         render_template('mail/new.html',
                                         email=user.email,
                                         confirm=url_for('auth.confirm',
                                                         _external=True,
                                                         token=confirm_token)))
        db.session.add(user)
        db.session.commit()
        user_dict = user.to_dict()
        resp = make_response(jsonify(user_dict))
        resp.headers['Location'] = user_dict['url']
        resp.status_code = 201
        return resp


api.add_resource(UsersApi, '/api/users')


class UserApi(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('email', type=str, required=True)
        self.reqparse.add_argument('password', type=str, required=True)
        super().__init__()

    @basic_auth.login_required
    def get(self, username):
        """
        获取用户信息
        :return:
        """
        user = User.query.filter_by(username=username).first()

        return user.to_dict() if user else ("Not found", 404)

    def put(self):
        """
        修改用户信息
        :return:
        """
        pass

    @basic_auth.login_required
    def delete(self, username):
        user = User.query.filter_by(username=username).first()
        if not user:
            return {'message': 'user not exists'}, 404
        db.session.delete(user)
        db.session.commit()

        return {'message': "user deleted successfully"}, 200


api.add_resource(UserApi, '/api/users/<username>')
