	#coding=utf-8
from flask import render_template, redirect, request, url_for, flash 
from . import auth
from .forms import LoginForm, RegistrationForm, SetPassword, ForgotPassword, RePassword, ResetEmail
from flask_login import login_user, login_required, logout_user, current_user
from ..models import User 
from .. import db
from ..email import send_email

@auth.route('/secret')
@login_required
def secret():
    return 'Only authenticated users are allowed!'

@auth.before_app_request
def before_request():
	if current_user.is_authenticated:
		current_user.ping()
		if current_user.is_authenticated and not current_user.confirmed and request.endpoint[:5] != 'auth.'  and request.endpoint != 'static':
			return redirect(url_for('auth.unconfirmed'))
		if "#" in current_user.username:
			logout_user()
			return render_template('ban-user.html')

@auth.route('/unconfirmed')
def unconfirmed():
	if current_user.is_anonymous or current_user.confirmed:
		return redirect(url_for('main.index'))
	return render_template('auth/unconfirmed.html')

@auth.route('/confirm')
@login_required
def resend_confirmation():
	token = current_user.generate_congirmation_token()
	send_email(current_user.email,u'验证邮箱','mail/confirm',user=current_user,token=token)
	flash(u'新的邮件已发送到你的邮箱，请注意查收')
	return redirect(url_for('main.index'))

@auth.route('/login',methods=['GET','POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user, form.remember_me.data)
			return redirect(request.args.get('next') or url_for('main.index'))
		flash(u'无效的用户名/密码')
	return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash(u'你已成功退出')
	return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET','POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		#user = User(email=form.email.data, username=form.username.data, password=form.password.data)
		user = User(email=form.email.data, username=form.username.data, password=form.password.data, confirmed=True)
		db.session.add(user)
		db.session.commit()
		token = user.generate_congirmation_token()
		send_email(user.email,u'验证邮箱','mail/confirm',user=user,token=token)
		#flash(u'验证邮件已发送到你所注册的邮箱，请及时确认哦～')
		flash(u'账号注册成功，可以登录啦~\(≧▽≦)/~')
		return redirect(url_for('auth.login'))
	return render_template('auth/register.html', form=form)

@auth.route('/cofirme/<token>')
@login_required
def confirm(token):
	if current_user.confirmed:
		return redirect(url_for('main.index'))
	if current_user.confirm(token):
		flash(u'验证邮箱通过！')
	else:
		flash(u'确认链接有效并且没有过期')
	return redirect(url_for('main.index'))

@auth.route('/repassword', methods=['GET','POST'])
@login_required
def reset_password():
	form  = SetPassword()
	if form.validate_on_submit():
		current_user.password = form.password.data 
		db.session.add(current_user)
		logout_user()
		flash(u'密码修改成功，请用新的密码登录吧')
		return redirect(url_for('auth.login'))
	return render_template('auth/setpassword.html', form=form)

@auth.route('/forgot_password', methods=['GET','POST'])
def forgot_password():
	form = ForgotPassword()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		token = user.generate_congirmation_token()
		send_email(user.email,u'【密码修改】验证邮件','mail/forgotpassword',user=user,token=token)
		flash(u'验证邮件已发送到你所注册的邮箱，请及时确认哦～')
		return redirect(url_for('main.index'))
	return render_template('auth/forgot_password.html', form=form)

@auth.route('/cofirme2/<token>', methods=['GET','POST'])
def confirm2(token):
	form = RePassword()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is None:
			flash(u'邮箱输入有误')
			return redirect(url_for('auth.confirm2', token=token))
		if user.confirm(token):
			flash(u'密码修改成功，请用新的密码登录吧')
			user.password = form.password.data
			db.session.add(user)
			return redirect(url_for('auth.login'))
		else:
			flash(u'确认链接有效并且没有过期')
			return redirect(url_for('main.index'))
	return render_template('auth/setpassword.html',form=form)

@auth.route('/reset_email', methods=['GET','POST'])
@login_required
def reset_email():
	form = ResetEmail()
	if form.validate_on_submit():
		#current_user.confirmed = False
		token = current_user.get_email_token(email=form.email.data)
		send_email(form.email.data,u'验证邮件','mail/reset_email',user = current_user.username,token=token)
		flash(u'验证邮件已发送')
		return redirect(url_for('main.index'))
	return render_template('auth/reset_email.html', form=form)

@auth.route('/confirme3/<token>')
@login_required
def confirme3(token):
	if current_user.email == current_user.check(token):
		flash(u'邮箱更改已生效')
		return redirect(url_for('main.index'))
	if current_user.check(token):
		current_user.email = current_user.check(token)
		db.session.add(current_user)
		flash(u'邮箱更改已生效')
		return redirect(url_for('main.index'))
	else:
		flash(u'确认链接有效并且没有过期')
		return redirect(url_for('main.index'))
