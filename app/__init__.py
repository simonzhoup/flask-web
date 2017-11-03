# coding=utf-8
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import DevelopmentConfig
from flask_login import LoginManager
from flask_pagedown import PageDown

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
pagedown = PageDown()
login_manager.session_protection = 'strong'  # 设置安全防护等级
login_manager.login_view = 'auth.login'  # 设置登录页面的端点
login_manager.login_message = u'继续操作请登录'


def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    DevelopmentConfig.init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    # 可选参数url_prefix代表，这个蓝本中所有的路由都会加上/auth前缀
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
