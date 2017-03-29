# -*- encoding=UTF-8 -*-

from  Yistagram import app,db
from  models import Image,User
from  flask import render_template,redirect,request,flash,get_flashed_messages
import random,hashlib

@app.route('/')
def index():
    images = Image.query.order_by('id desc').limit(10).all()
    return render_template('index.html',images=images)

@app.route('/image/<int:image_id>/')
def image(image_id):
    image = Image.query.get(image_id)
    if image == None:
        return redirect('/')
    return  render_template('pageDetail.html', image = image)

@app.route('/profile/<int:user_id>')
def profile(user_id):
    user = User.query.get(user_id)
    if user == None:
        return redirect('/')
    return render_template('/profile.html', user = user)

@app.route('/reloginpage')
def regloginpage():
    return render_template('/login.html')

def redirect_with_msg(target,msg,category):
    if msg != None:
        flash(msg,category=category)
    return redirect(target)

@app.route('/reg/', methods={'post', 'get'})
def reg():
    #request.args url里的参数
    #request.form post里的参数，value自动选择
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()

    if username == '' or password == '':
        redirect_with_msg('/reloginpage/',u'用户名或密码为空','relogin')

    user = User.query.filter_by(username=username).first()

    if user != None:
        redirect_with_msg('/reloginpage/',u'用户名已存在','relogin')

    #更多判断

    salt = '.'.join(random.sample('0123456789abcdefghijklmnopqrstABCDEFGHIJKLMNOPQRSTUVWXYZ',10))
    m = hashlib.md5()
    m.update(password+salt)
    password = m.hexdigest()
    user = User(username, password, salt)
    db.session.add(user)
    db.session.commit()

    return  redirect('/')


