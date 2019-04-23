from flask import Blueprint, flash, render_template, request, jsonify
from .models import User
from .extensions import db, basic_auth, token_auth
import time

auth = Blueprint('auth', __name__)


@auth.route('/confirm/<token>')
def confirm(token):
    user_id = User.confirm(token)
    if not user_id:
        flash('The confirmation link is invalid or has expired.', 'danger')
    user = User.query.filter_by(id=user_id).first_or_404()
    if user.confirmed:
        flash('Account already confirmed. Please login.', 'success')
    else:
        user.confirmed = True
        db.session.add(user)
        db.session.commit()
        flash('You have confirmed your account.Thx!', 'success')
    return "main page"

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user:
        authenticate = user.verify_password(data['password'])
        if authenticate:
            if not user.confirmed:
                pass
            user.ping()
            db.session.commit()

            token = user.generate_auth_token(expiration=3600)
            user_data = {
                'tokens': {
                    'token': token,
                    'expiration': 3600,
                    'timestamp': time.time() * 1000,
                },
                'user': {
                    'username': user.username,
                    'avatar': user.gravatar()
                }
            }
            return jsonify(user_data)
        else:
            return jsonify({'message': 'invalid password'}), 401
    return jsonify({'message': 'invalid email'})
