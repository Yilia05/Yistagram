# -*- encoding=UTF-8 -*-

from  Yistagram import app
from  models import Image,User
from  flask import render_template

@app.route('/')
def index():
    images = Image.query.order_by('id desc').limit(10).all()
    return render_template('index.html',images=images)
