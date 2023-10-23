from flask import Flask, request
from flask import render_template, url_for, redirect
from flask import current_app as app 
from application.models import *

@app.route("/", methods = ['GET', 'POST'])
def home_page():
    if request.method == 'GET' :
        return render_template('home.html')
    if request.method == 'POST' :
        return url_for(registration)

@app.route("/register", methods = ['GET', 'POST'])
def registration():
    if request.method == 'GET' :
        return render_template('usr_reg.html')
    if request.method == 'POST' :
        return render_template('user_dashboard.html')
    
@app.route("/user_login", methods = ['GET', 'POST'])
def user_login():
    if request.method == 'GET' :
        return render_template('usr_login.html')
    if request.method == 'POST' :
        return render_template('user_dashboard.html')

@app.route("/admin_login", methods = ['GET', 'POST'])
def admin_login():
    if request.method == 'GET' :
        return render_template('admn_login.html')
    if request.method == 'POST' :
        return render_template('user_dashboard.html')