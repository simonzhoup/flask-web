#coding=utf-8
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, EqualTo, Regexp
from wtforms import ValidationError
from ..models import User
from flask_login import current_user

class LoginForm(FlaskForm):
	email = StringField(u'邮箱',validators=[Required(),Length(1,64),Email()])
	password = PasswordField(u'密码', validators=[Required(),Length(1,64)])
	remember_me = BooleanField(u'记住我')
	submit = SubmitField(u'登录')

class RegistrationForm(FlaskForm):
	email = StringField(u'邮箱', validators=[Required(), Length(1,64),Email()])
	username = StringField(u'用户名', validators=[Required(), Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'Username must have only letters,''numbers, dots or underscor.')])
	password = PasswordField(u'密码', validators=[Required(),EqualTo('password2', message=u'密码不一致')])
	password2 = PasswordField(u'确认密码', validators=[Required()])
	submit = SubmitField(u'注册')

	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError(u'邮箱已注册')

	def validate_username(self, field):
		if User.query.filter_by(username=field.data).first():
			raise ValidationError(u'用户名已存在')


class SetPassword(FlaskForm):
	oldpassword = PasswordField(u'旧的密码', validators=[Required()])
	password = PasswordField(u'输入新密码吧', validators=[Required(),EqualTo('password2',message=u'两次密码好像不一致哦')])
	password2 = PasswordField(u'确认新密码', validators=[Required()])
	submit = SubmitField(u'提交')

	def validate_oldpassword(self, field):
		if not current_user.verify_password(field.data):
			raise ValidationError(u'密码错误')

class ForgotPassword(FlaskForm):
	email = StringField(u'告诉我你的注册邮箱', validators=[Required(),Length(1,64),Email()])
	submit = SubmitField(u'提交')

	def validate_email(self, field):
		if not User.query.filter_by(email=field.data).first():
			raise ValidationError(u'你输入的邮箱不存在')

class RePassword(FlaskForm):
	email = StringField(u'要更改密码的邮箱', validators=[Required(),Length(1,64),Email()])
	password = PasswordField(u'输入新密码吧', validators=[Required(),EqualTo('password2',message=u'两次密码好像不一致哦')])
	password2 = PasswordField(u'确认新密码', validators=[Required()])
	submit = SubmitField(u'提交')

class ResetEmail(FlaskForm):
	email = StringField(u'告诉我你要使用的新邮箱', validators=[Required(),Length(1,64),Email()])
	submit = SubmitField(u'提交')

	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError(u'这个邮箱已经注册过了')
