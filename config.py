# coding=utf-8
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'simon'
    #SQLALCHEMY_DATABASE_URI = 'mysql://root:1234@localhost:3306/flask'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'Flasky Admin <540918220@qq.com>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN') or '540918220@qq.com'
    UPLOAD_FOLDER = '/uploadimg'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
        os.path.join(basedir, 'data.sqlite')
    TOPICS = [u'互联网', u'创业', u'消费电子产品', u'游戏',
              u'美食', u'旅行', u'音乐', u'电影', u'健康']
