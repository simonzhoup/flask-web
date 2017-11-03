# coding=utf-8
from flask import current_app
from flask_wtf import FlaskForm
from flask_uploads import UploadSet, IMAGES
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField, FileField
from wtforms.validators import Required, Length, Email, Regexp
from flask_wtf.file import FileAllowed, FileRequired
from flask_pagedown.fields import PageDownField
from ..models import Role, User
from wtforms import ValidationError

images = UploadSet('images', IMAGES)


class NameForm(FlaskForm):
    name = StringField(u'请告诉我你的名字:', validators=[Required()])
    submit = SubmitField(u'提交')


class EditUser(FlaskForm):
    name = StringField(u'真实姓名', validators=[Length(0, 64)])
    location = StringField(u'住址', validators=[Length(0, 64)])
    about_me = TextAreaField(u'个人介绍')
    submit = SubmitField(u'提交')


class EditAdmin(FlaskForm):
    email = StringField(u'邮箱', validators=[Required(), Length(1, 64), Email()])
    username = StringField(u'用户名', validators=[Required(), Length(1, 64), Regexp(
        '^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Username must have only letters,''numbers, dots or underscor.')])
    confirmed = BooleanField(u'验证状态')
    role = SelectField(u'用户组', coerce=int)
    name = StringField(u'真实姓名', validators=[Length(0, 64)])
    location = StringField(u'住址', validators=[Length(0, 64)])
    about_me = TextAreaField(u'个人介绍')
    submit = SubmitField(u'提交')

    def __init__(self, user, *args, **kwargs):
        super(EditAdmin, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError(u'邮箱已注册')

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已存在')


class Edit(FlaskForm):
    head_img = FileField(u'<h1>题图</h1>', validators=[FileRequired()])
    head = TextAreaField(u'<h1>标题</h2>', validators=[Required()])
    body = TextAreaField(u'<h2>正文</h2>', validators=[Required()])
    topic = SelectField(u'主题')
    submit = SubmitField(u'提交')

    def __init__(self, *args, **kwargs):
        super(Edit, self).__init__(*args, **kwargs)
        self.topic.choices = [(j, i)
                              for i, j in zip(current_app.config['TOPICS'], current_app.config['TOPICS'])]


class CommentForm(FlaskForm):
    body = TextAreaField(u'写评论', validators=[Required()])
    submit = SubmitField(u'提交')


class UploadPhoto(FlaskForm):
    photo = FileField(u'选择头像', validators=[Required()])
    submit = SubmitField(u'提交')


class UlockUser(FlaskForm):
    email = StringField(u'邮箱', validators=[Required(), Email()])
    submit = SubmitField(u'提交')

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if user is None or "#" not in user.username:
            raise ValidationError(u'请输入正确的邮箱')
