# -*- coding: utf-8 -*-
from flask import g, jsonify, session
from . import api
from ..extensions import basic_auth, token_auth, db
from ..models import User


@api.route('/api/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    token = g.current_user.generate_confirmation_token(expiration=3600)

    return jsonify({
        'token': token,
        'expiration': 3600
    }), 200


@basic_auth.verify_password
def verify_password(email, password):
    user = User.query.filter_by(email=email).first()
    if user is None:
        return False
    g.current_user = user
    return user.verify_password(password)


@basic_auth.error_handler
def basic_auth_error():
    return 'Invalid credentials'


@token_auth.verify_token
def verify_token(token):
    g.current_user = User.verify_auth_token(token) if token else None
    if g.current_user:
        g.current_user.ping()
        db.session.commit()
    return g.current_user is not None
