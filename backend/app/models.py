from .extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import url_for, current_app, abort
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, \
    SignatureExpired, BadSignature
from .utils import timestamp, domain, weekday, init_schedule
import os
from celery.schedules import crontab
import pickle
import hashlib


user_subscription = db.Table('user_subscription',
                             db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                             db.Column('subscription_id', db.Integer, db.ForeignKey('subscriptions.id'))
                             )


class UserVideo(db.Model):
    __tablename__ = 'user_video'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), primary_key=True)
    # `finished`有True或False两种状态，当video.address_type等于'playable'时表示观看或未观看
    # 当video.address_type等于'downloadable'时表示已下载或未下载
    finished = db.Column(db.Boolean, default=False)
    video = db.relationship('Video', back_populates="users")
    user = db.relationship('User', back_populates='videos')
    subs_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'), primary_key=True)
    subscription = db.relationship('Subscription')

    @property
    def _video(self):
        self.video.finished = self.finished
        return self.video

    def video_to_dict(self):
        video = self._video
        d = {
            'id': video.id,
            'title': video.title,
            'address': video.address,
            'finished': self.video.finished,
            'url': url_for('videoapi', _external=True, username=self.user.username, video_id=self.video_id)
        }
        return d

    def switch_finished(self):
        self.finished = not self.finished
        db.session.commit()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), nullable=False, unique=True)
    email = db.Column(db.String(32), unique=True, nullable=False)
    subscriptions = db.relationship('Subscription',
                                    secondary=user_subscription,
                                    lazy='dynamic')
    password_hash = db.Column(db.String(256))
    avatar_hash = db.Column(db.String(32))
    login_count = db.Column(db.Integer, default=0)
    member_since = db.Column(db.Integer, default=timestamp)
    last_seen = db.Column(db.Integer, default=timestamp, onupdate=timestamp)
    confirmed = db.Column(db.Boolean, default=False)
    videos = db.relationship('UserVideo', back_populates='user', lazy='dynamic')

    def add_video(self, video, fetcher):
        uv = UserVideo()
        uv.video = video
        subscription = fetcher.subscription
        uv.subscription = subscription
        self.videos.append(uv)
        fetcher.videos.append(video)
        db.session.add_all([self, subscription])

    @staticmethod
    def create(data):
        user = User()
        user.from_dict(data, partial_update=False)
        user.avatar_hash = hashlib.md5(user.email.encode('utf-8')).hexdigest()
        return user

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """在给password赋值时计算密码的散列值"""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expiration=600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id}).decode()

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except (SignatureExpired, BadSignature):
            return None
        user = User.query.get(data['id'])
        return user

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({'confirm': self.id})

    @staticmethod
    def confirm(token):
        token = token.encode()
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        user_id = data['confirm']
        return user_id

    def ping(self):
        self.last_seen = timestamp()
        self.login_count += 1
        db.session.add(self)

    def gravatar(self, size=100, default='identicon', rating='g'):
        url = 'https://secure.gravatar.com/avatar'
        if self.avatar_hash:
            _hash = self.avatar_hash
        else:
            _hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=_hash, size=size, default=default, rating=rating
        )

    def from_dict(self, data, partial_update=True):
        for field in ['email', 'password', 'username']:
            try:
                setattr(self, field, data[field])
            except KeyError:
                if not partial_update:
                    abort(400)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'member_since': str(self.member_since),
            'last_seen': str(self.last_seen),
            'subscriptions': url_for('subscribeapi', _external=True, username=self.username),
            'url': url_for('userapi', _external=True, username=self.username),
        }

    def user_subs_videos(self, subs):
        user_videos = self.videos.filter_by(subscription=subs).all()
        if not user_videos:
            return
        d = {
            'download': [],
            'play': []
        }
        for uv in user_videos:
            if uv.video.fetcher.address_type == 'downloadable':
                d['download'].append(uv.video_to_dict())
            else:
                d['play'].append(uv.video_to_dict())
        return d

    def __repr__(self):
        return "<User(email='%s')>" % self.email


class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), unique=True)
    user_count = db.Column(db.Integer)
    ended = db.Column(db.Boolean, default=False)
    users = db.relationship('User', secondary=user_subscription, lazy='dynamic')
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'))
    create_at = db.Column(db.Integer, default=timestamp)
    fetchers = db.relationship('Fetcher', lazy='dynamic', backref='subscription')

    def add_one_user(self):
        """
        给订阅者数目加一
        """
        if self.user_count is None:
            self.user_count = 0
        self.user_count += 1

    def is_ended(self):
        if self.ended:
            return
        is_ended_ = list(filter(lambda s: s.ended, self.fetchers))
        if is_ended_:
            self.ended = True

    @property
    def _timestamp(self):
        pass

    @_timestamp.getter
    def _timestamp(self):
        return datetime.fromtimestamp(self.create_at)

    def to_dict(self, username=None, include_poster=False, include_title=False):
        """
        :param username: 返回用户订阅信息时提供`username`，其它时机无需提供
        :param include_poster: 添加订阅时返回不包含poster的订阅信息
        :param include_title: 添加订阅时不返回包含title的订阅信息
        :return:
        """
        subs = {
            'id': self.id,
            'title': self.movie.title,
            'synopsis': self.movie.synopsis,
            # 'urls': [f.url for f in self.fetchers],
            'user_count': self.user_count,
            'create_at': str(self._timestamp),
            'episode_aired': self.movie.episode_aired,
            'episode_count': self.movie.episode_count,
            'refes': {r.second_level_domain: r.url for r in self.movie.refes}
        }
        if not include_poster and not include_title:
            return subs

        poster_path = self.movie.poster_path
        if poster_path.startswith('http'):
            poster = poster_path
        else:
            try:
                name = os.path.basename(self.movie.poster_path)
            except TypeError:
                poster = None
            else:
                poster = url_for('static', _external=True, filename='posters/'+name)
        subs.update({'poster': poster, 'title': self.movie.title})

        if username is None:
            return subs

        subs.update({
            'videos': url_for(
                'videosapi', _external=True, username=username, subs_id=self.id)})
        return subs

    def url(self, user):
        """
        获取用户的subscription_url
        :param user: instance of `User`
        """
        if self.users.filter_by(email=user.email).first():
            return url_for('subscriptionapi',
                           _external=True,
                           username=user.username,
                           sub_id=self.id)

    def __repr__(self):
        if self.movie:
            return "<Subscription(title='{}')>".format(self.movie.title)
        else:
            return "<Subscription(id='{}')>".format(self.id)


class Fetcher(db.Model):
    __tablename__ = 'fetchers'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(128))
    ended = db.Column(db.Boolean, default=False)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'))
    address_type = db.Column(db.String(32))
    fetch_records = db.relationship('FetchRecord', backref='fetcher')
    videos = db.relationship('Video', lazy='dynamic', backref='fetcher')
    current_schedule = db.Column(db.PickleType)
    adjusted_schedule = db.Column(db.Boolean, default=False)

    @property
    def schedule(self):
        pass

    @schedule.setter
    def schedule(self, _schedule):
        self.current_schedule = pickle.dumps(_schedule)

    @schedule.getter
    def schedule(self):
        return pickle.loads(self.current_schedule)

    @classmethod
    def create(cls, url):
        f = cls()
        f.url = url
        f.schedule = init_schedule()
        return f

    def is_ended(self):
        if self.ended:
            return True
        if self.videos.count() >= self.subscription.movie.episode_count:
            self.ended = True
            return True

    def should_adjust(self):
        """

        """
        if self.fetch_records.count() >= 21 and not self.adjusted_schedule:
            schedule = self.estimated_update_cycle()
            return schedule

    def fetch_record_stats(self):
        """
        统计抓取记录
        :return: 以 weekday/updated_count 为键值对的字典
            In : weeks = [i for i in range(7)] * 3
            In : fetch_records = []
            In : for w in weeks:
            ...     if w == 3 or w == 5:
            ...         fr = FetchRecord(updated=True, weekday=w)
                    else:
                        fr = FetchRecord(weekday=w)
                    fetch_records.append(fr)
            In : fetch_record_stats()
            out: {0: 0, 1: 0, 2: 0, 3: 3, 4: 0, 5: 3, 6: 0}
                                    ^  ^        ^  ^
        """
        d = dict()
        fetch_records = self.fetch_records
        for fr in fetch_records:
            _weekday = fr.weekday
            if _weekday not in d:
                d[_weekday] = 0
            if fr.updated:
                d[_weekday] += 1

        return d

    def estimated_update_cycle(self):
        """
        估计更新周期。例如：fetch_record_stats={0: 0, 1: 0, 2: 0, 3: 3, 4: 0, 5: 3, 6: 0}
        那么更新周期为每周星期二和四，需要在更新记录累计一定数量后调用
        :return: celery.schedules.crontab
        """
        stats = self.fetch_record_stats()
        weekdays = set()
        for _weekday, count in stats.items():
            if count != 0:
                weekdays.add(_weekday)
        self.schedule = crontab(hour=0, day_of_week=weekdays)
        self.adjusted_schedule = True
        return self.schedule

    def postponed_update(self):
        """
        延期更新。当电视剧没有在估计的周期中更新时调用，
        <crontab: * 0 {3, 5} * * (m/h/d/dM/MY)> =>
        <crontab: * 0 {3, 4, 5, 6} * * (m/h/d/dM/MY)>
        :return: celery.schedules.crontab
        """
        _weekday = self.schedule.day_of_week
        new_weekdays = set()
        for wd in _weekday:
            new_weekdays.add(wd)
            _wd = wd + 1
            if _wd < 7:
                new_weekdays.add(_wd)
            else:
                new_weekdays.add(0)
        self.schedule = crontab(hour=0, day_of_week=new_weekdays)
        return self.schedule

    def __repr__(self):
        return '<Fetcher(url={})>'.format(self.url)


class FetchRecord(db.Model):
    __tablename__ = 'fetch_record'
    id = db.Column(db.Integer, primary_key=True)
    updated = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.Integer)
    weekday = db.Column(db.Integer)
    schedule = db.Column(db.String(64))
    fetcher_id = db.Column(db.Integer, db.ForeignKey('fetchers.id'))

    @property
    def _timestamp(self):
        pass

    @_timestamp.getter
    def _timestamp(self):
        return datetime.fromtimestamp(self._timestamp)

    @classmethod
    def create(cls, schedule, updated=False):
        fr = cls()
        fr.timestamp = timestamp()
        if updated:
            fr.updated = updated
        fr.schedule = schedule
        fr.weekday = weekday(fr.timestamp)
        return fr


class Video(db.Model):
    __tablename__ = 'videos'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    address = db.Column(db.String(512), unique=True)
    fetcher_id = db.Column(db.Integer, db.ForeignKey('fetchers.id'))
    timestamp = db.Column(db.Integer, default=timestamp)
    users = db.relationship('UserVideo', back_populates='video')
    finished = None

    @property
    def _timestamp(self):
        pass

    @_timestamp.getter
    def _timestamp(self):
        return datetime.fromtimestamp(self.timestamp)

    def to_dict(self, with_user=False):
        return {
            'id': self.id,
            'title': self.title,
            'address': self.address,
            'create_at': str(self._timestamp),
        }

    def __repr__(self):
        return "<Video(title='{}')>".format(self.title)


class Search(db.Model):
    __tablename__ = 'search'
    id = db.Column(db.Integer, primary_key=True)
    keywords = db.Column(db.String(128))
    timestamp = db.Column(db.Integer, default=timestamp)
    hit = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'keywords': self.keywords,
            'hit': self.hit,
            'timestamp': self.timestamp,
        }

    def __repr__(self):
        return "<Search(content='{}')>".format(self.content)


class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), unique=True)
    poster_path = db.Column(db.String(128), unique=True)
    episode_aired = db.Column(db.String(32))
    episode_count = db.Column(db.Integer)
    refes = db.relationship('Refe')
    synopsis = db.Column(db.String(256))
    subscription = db.relationship('Subscription', uselist=False, backref='movie')

    def to_dict(self, videos=True):
        try:
            name = os.path.basename(self.poster_path)
        except TypeError:
            name = None
        refes = {}
        for refe in self.refes:
            refes.update(refe.to_dict())

        d = {
            'id': self.id,
            'title': self.title,
            'synopsis': self.synopsis[:188],
            'poster': url_for('static', _external=True, filename='posters/'+name) if name else None,
            'episode_aired': self.episode_aired,
            'episode_count': self.episode_count,
            'ended': self.subscription.ended,
            'refes': refes,
        }
        if videos:
            downloadable_videos = self.subscription.fetchers.\
                filter_by(address_type='downloadable').first().\
                videos.all()
            playable_videos = self.subscription.fetchers.\
                filter_by(address_type='playable').first().\
                videos.all()
            d.update({            
                'videos': {
                    'downloadable': [v.to_dict() for v in downloadable_videos],
                    'playable': [v.to_dict() for v in playable_videos]
                }})
        return d

    @classmethod
    def create(cls, data):
        movie = cls()
        movie.from_dict(data)
        movie.synopsis = movie.synopsis[:256]
        return movie

    def from_dict(self, data):
        for k, v in data.items():
            if k == 'synopsis':
                v = v[:256]
            refes = []
            if k == 'refes':
                for kk, vv in v.items():
                    refe = Refe()
                    refe.second_level_domain = kk
                    for kkk, vvv in vv.items():
                        setattr(refe, kkk, vvv)
                    refes.append(refe)

            setattr(self, k, refes or v)


class Refe(db.Model):
    __tablename__ = 'refes'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(64))
    second_level_domain = db.Column(db.String(16))
    rating_value = db.Column(db.Float, nullable=True)
    rating_count = db.Column(db.Integer, nullable=True)
    fetchable = db.Column(db.Boolean, default=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'))

    def __repr__(self):
        return '<Refe(url={})>'.format(self.url)

    def to_dict(self):
        d = {
            self.second_level_domain: {
                'url': self.url
            }
        }
        if not self.fetchable:
            d[self.second_level_domain].update(
                {
                    'rating_value': self.rating_value,
                    'rating_count': self.rating_count,
                }
            )

        return d
