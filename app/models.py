# coding=utf-8
from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from flask import current_app
from . import db


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES | Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    head_img = db.Column(db.String(64), default='head_img/flasky.ico')
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    topics = db.Column(db.String(64), default='')

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
    # 检查管理员

    def can(self, permissions):
        return self.role_id is not None and self.role_id == permissions

    def is_administrator(self):
        return self.role.name == "Administrator"

    @property
    def password(self):
        raise AttributeError(u'密码属性不可读')

    # 生成密码hash值
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # 验证密码
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_congirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def get_email_token(self, email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id, 'email': email})

    def check(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        #self.confirmed = True
        db.session.add(self)
        return data.get('email')

    def follow(self, user):
        if not self.following(user):
            f = Follow(follow_from=self.id, follow_to=user.id)
            db.session.add(f)

    def following(self, user):
        return Follow.query.filter_by(follow_from=self.id, follow_to=user.id).first()

    def unfollow(self, user):
        f = self.following(user)
        if f:
            db.session.delete(f)

    def is_self(self, user):
        return self.username == user.username

    def delete_user(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):

    def can(self, Permission):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    post_head = db.Column(db.Text)
    post_img = db.Column(db.String(64))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    count = db.Column(db.Integer, default=0)
    topics = db.Column(db.String(64))


class Follow(db.Model):
    __tablename__ = 'follows'
    follow_from = db.Column(db.Integer, primary_key=True, index=True)
    follow_to = db.Column(db.Integer, primary_key=True, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    commentator = db.Column(db.String(64))
    body = db.Column(db.Text)
    post_id = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)


# class Topics_user(db.Model):
#     __tablename__ = 'topics_user'
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, index=True)
#     # suoyou = db.Column(db.Boolean, default=True, index=True)
#     hulianwang = db.Column(db.Boolean, default=False, index=True)
#     chuangye = db.Column(db.Boolean, default=False, index=True)
#     dianzi = db.Column(db.Boolean, default=False, index=True)
#     youxi = db.Column(db.Boolean, default=False, index=True)
#     meishi = db.Column(db.Boolean, default=False, index=True)
#     lvxing = db.Column(db.Boolean, default=False, index=True)
#     yinyue = db.Column(db.Boolean, default=False, index=True)
#     dianyin = db.Column(db.Boolean, default=False, index=True)
#     jiankang = db.Column(db.Boolean, default=False, index=True)
