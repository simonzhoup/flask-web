# coding=utf-8
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')
import os
import json
from datetime import datetime
from flask import Flask, current_app, render_template, session, redirect, url_for, flash, request, Response, abort, jsonify, make_response
from . import main
from .forms import NameForm, EditUser, EditAdmin, Edit, CommentForm, UploadPhoto, UlockUser
from .. import db
from ..models import User, Role, Post, Follow, Comment
from ..email import send_email
from flask_login import current_user, login_required
from sqlalchemy import and_
from lxml import etree
import requests


ALLOWED_FILE = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'jif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_FILE


@main.route('/', methods=['GET', 'POST'])
def index():
    name = None
    if current_user.is_authenticated:
        name = current_user.username
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    url = "https://bing.ioliu.cn/?p=1"
    xx = requests.get(url).text
    xx = etree.HTML(xx)
    image_url = xx.xpath(u'//div[@class="container"]/div/div/img/@data-progressive')
    return render_template('index.html', name=name, posts=posts, Comment=Comment,image_url=image_url[0:3])


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    following = Follow.query.filter_by(follow_from=user.id).count()
    follower = Follow.query.filter_by(follow_to=user.id).count()
    return render_template('user.html', user=user, posts=posts, following=following, follower=follower, Comment=Comment)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditUser()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash(u'你的资料已更新')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile-admin/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_profile_admin(id):
    if not current_user.is_administrator():
        print 'jjj'
        return redirect(url_for('.index'))
    user = User.query.get_or_404(id)
    form = EditAdmin(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash(u'用户资料已变更')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit-profile-admin.html', form=form)


@main.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = Edit()
    if form.validate_on_submit():
        img = form.head_img.data
        post = Post(post_head=form.head.data, body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        img.save('app/static/posts/imgs/%s.jpg' % post.id)
        post.post_img = 'posts/imgs/%s.jpg' % post.id
        db.session.add(post)
        return redirect(url_for('.index'))
    return render_template('edit.html', form=form)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.filter_by(id=id).first()
    post.count += 1
    db.session.add(post)
    form = CommentForm()
    if post is None:
        abort(404)
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash(u'请登录后发表评论')
            return redirect(url_for('auth.login'))
        else:
            comment = Comment(commentator=current_user.username,
                              body=form.body.data, post_id=post.id)
            db.session.add(comment)
            return redirect(url_for('.post', id=post.id, form=form))
    comments = Comment.query.filter_by(
        post_id=id).order_by(Comment.timestamp.desc()).all()
    return render_template('post.html', post=post, form=form, comments=comments, User=User)


@main.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    if current_user.is_self(user):
        flash(u'不能关注自己')
        return redirect(url_for('.index'))
    current_user.follow(user)
    flash(u'你已成功关注%s' % user.username)
    return redirect(url_for('.user', username=user.username))


@main.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    current_user.unfollow(user)
    flash(u'你已取消关注%s' % user.username)
    return redirect(url_for('.user', username=user.username))


@main.route('/user/follower/<username>')
@login_required
def follower(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    followers = Follow.query.filter_by(
        follow_to=user.id).order_by(Follow.timestamp.desc()).all()

    return render_template('follower.html', username=username, followers=followers, User=User)


@main.route('/user/following/<username>')
@login_required
def following(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    followings = Follow.query.filter_by(
        follow_from=user.id).order_by(Follow.timestamp.desc()).all()
    return render_template('following.html', username=username, followings=followings, User=User)


@main.route('/upload-photo', methods=['GET', 'POST'])
@login_required
def upload_photo():
    form = UploadPhoto()
    if form.validate_on_submit():
        file = form.photo.data
        if file and allowed_file(file.filename):
            file.save(current_app.config[
                      'UPLOAD_FOLDER'] + '%s.jpg' % current_user.id)
            current_user.head_img = 'head_img/%s.jpg' % current_user.id
            db.session.add(current_user)
            flash(u'头像修改成功')
        else:
            flash(u'请检查文件是否存在并合法。')
        return redirect(url_for('.user', username=current_user.username))
    return render_template('upload-photo.html', form=form)


@main.route('/editpost/<int:id>', methods=['GET', 'POST'])
@login_required
def editpost(id):
    post = Post.query.get_or_404(id)
    form = Edit(post=post)
    if post is None or post.author != current_user and not current_user.is_administrator():
        return redirect(url_for('.index'))
    if form.validate_on_submit():
        img = form.head_img.data
        post.post_head = form.head.data
        post.body = form.body.data
        post.topics = form.topic.data
        img.save('app/static/posts/imgs/%s.jpg' % post.id)
        post.post_img = 'posts/imgs/%s.jpg' % post.id
        db.session.add(post)
        return redirect(url_for('.index'))
    #form.head_img.data = post.post_img
    form.head.data = post.post_head
    form.body.data = post.body
    form.topic.data = post.topics
    return render_template('edit.html', form=form)


@main.route('/user-manage')
@login_required
def user_manage():
    if not current_user.is_administrator():
        flash(u'你没有权限')
        return redirect(url_for('.index'))
    users = User.query.order_by(User.member_since.desc()).all()
    return render_template('user-manage.html', users=users)


@main.route('/delete-user/<int:id>')
@login_required
def delete_user(id):
    if not current_user.is_administrator():
        flash(u'你没有权限')
        return redirect(url_for('.index'))
    user = User.query.get_or_404(id)
    follows = Follow.query.filter_by(follow_from=user.id).all()
    for follow in follows:
        db.session.delete(follow)
    followeds = Follow.query.filter_by(follow_to=user.id).all()
    for followed in followeds:
        db.session.delete(followed)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('.user_manage'))


@main.route('/ban-user/<int:id>')
@login_required
def ban_user(id):
    if not current_user.is_administrator():
        flash(u'你没有权限')
        return redirect(url_for('.index'))
    user = User.query.get_or_404(id)
    user.username = '#ban#' + user.username
    db.session.add(user)
    return redirect(url_for('.user_manage'))


@main.route('/unlock', methods=['GET', 'POST'])
def unlock():
    form = UlockUser()
    if form.validate_on_submit():
        send_email(to=current_app.config[
                   'FLASKY_ADMIN'], subject=u'账号解锁', template='mail/unlock', email=form.email.data)
        flash(u'邮件已发送')
        return redirect(url_for('.index'))
    return render_template('unlock.html', form=form)


@main.route('/unlock-user/<int:id>')
@login_required
def unlock_user(id):
    if not current_user.is_administrator():
        return redirect(url_for('.index'))
    user = User.query.get_or_404(id)
    user.username = user.username.strip('#ban#')
    db.session.add(user)
    return redirect(url_for('.user_manage'))


@main.route('/topics', methods=['GET', 'POST'])
def topics():
    topics = current_app.config['TOPICS']
    show_topics = request.cookies.get('show_topics', '')
    if show_topics:
        posts = Post.query.filter_by(topics=show_topics).all()
    elif current_user.is_authenticated:
        # topics_list = (current_user.topics).split('/')
        # rule = and_(*[Post.topics.like(w) for w in topics_list])
        # posts = Post.query.filter(rule)
        posts = Post.query.all()
    else:
        posts = None
    return render_template('topics.html', topics=topics, show_topics=show_topics, posts=posts, Comment=Comment, user=current_user)


@main.route('/www/<who>', methods=['GET', 'POST'])
def show_topics(who):
    resp = make_response(redirect(url_for('.topics')))
    resp.set_cookie('show_topics', who, max_age=2)
    return resp


@main.route('/topics/<topic>')
@login_required
def user_topics(topic):
    current_user.topics += topic + '/'
    db.session.add(current_user)
    flash(u'你已成功关注话题%s' % topic)
    return redirect(url_for('.topics'))


@main.route('/untopic/<topic>')
@login_required
def untopic(topic):
    if topic in current_user.topics:
        a = topic + '/'
        current_user.topics = current_user.topics.replace(a, '')
        db.session.add(current_user)
    return redirect(url_for('.topics'))

