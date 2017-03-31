# -*- encoding=UTF-8 -*-
#flask mail库可以给用户发邮件
from Yistagram import app, db
from models import Image, User
from flask import render_template, redirect, request, flash, get_flashed_messages
import random, hashlib, json
from flask_login import login_user, logout_user, current_user, login_required

@app.route('/')
def index():
    images = Image.query.order_by('id desc').limit(10).all()
    return render_template('index.html', images=images)

@app.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    user = User.query.get(user_id)
    if user == None:
        return redirect('/')
    paginate = Image.query.filter_by(user_id=user_id).paginate(page=1, per_page=3, error_out=False)
    return render_template('/profile.html', user=user, Image=paginate.items)

@app.route('/profile/images/<int:user_id>/<int:page>/<int:per_page>')
def user_images(user_id, page, per_page):
    paginate = Image.query.filter_by(user_id=user_id).paginate(page=page, per_page=3, error_out=False)
    map = {'has_next': paginate.has_next}
    images = []
    for image in paginate.items:
        imgvo = {'id':image.id, 'url':image.url, 'comment_count':len(image.comments)}
        images.append(imgvo)

    map['images'] = images

    return json.dumps(map)

@app.route('/reloginpage/')
def reloginpage():
    if current_user.is_authenticated:
        return redirect('/')
    msg = ''
    for m in get_flashed_messages(with_categories=False, category_filter=['relogin']):
        msg = msg + m
    return render_template('login.html', msg=msg, next=request.values.get('next'))

def redirect_with_msg(target,msg,category):
    if msg != None:
        flash(msg, category=category)
    return redirect(target)


@app.route('/login/', methods={'get', 'post'})
def login():
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()
    # 校验
    user = User.query.filter_by(username=username).first()
    if username == '' or password == '':
        return redirect_with_msg('/reloginpage', u'用户名和密码不能为空', 'relogin')

    if user == None:
        return redirect_with_msg('/reloginpage', u'用户名不存在', 'relogin')

    m = hashlib.md5()
    m.update(password + user.salt)
    if m.hexdigest() != user.password:
        return redirect_with_msg('/reloginpage', u'密码错误', 'relogin')

    login_user(user)

    next = request.values.get('next')
    if next != None and next.startswith('/') > 0:
        return redirect(next)

    return redirect('/')

@app.route('/reg/', methods={'post', 'get'})
def reg():
    #request.args url里的参数
    #request.form post里的参数，value自动选择
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()
    user = User.query.filter_by(username=username).first()

    if username == '' or password == '':
        return redirect_with_msg('/reloginpage/', u'用户名或密码为空','relogin')

    if user != None:
        return redirect_with_msg('/reloginpage/', u'用户名已存在','relogin')

    #更多判断

    salt = '.'.join(random.sample('0123456789abcdefghijklmnopqrstABCDEFGHIJKLMNOPQRSTUVWXYZ',10))
    m = hashlib.md5()
    m.update(password+salt)
    password = m.hexdigest()

    #提交新注册到user数据库
    user = User(username, password, salt)
    db.session.add(user)
    db.session.commit()

    login_user(user)

    return redirect('/')

@app.route('/logout/')
def logout():
    logout_user()
    return redirect('/')


