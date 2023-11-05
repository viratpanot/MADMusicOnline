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
        user = User(
            firstname =request.form["firstname"],
            lastname =request.form["lastname"],
            continent = request.form["continents"],
            email=request.form["email"],
            password =request.form["password"],
            )
        password =request.form["password"]
        confirmpassword =request.form["confirmpassword"]
        if (password==confirmpassword):
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("user_login"))
        else :
             return render_template('passwordvalidation.html')


@app.route("/user_login", methods = ['GET', 'POST'])
def user_login():
    if request.method == 'GET' :
        return render_template('usr_login.html')
    if request.method == 'POST' :
        return render_template('user_dashboard.html', email=request.form['email'], password =request.form["password"] )

@app.route("/admin_login", methods = ['GET', 'POST'])
def admin_login():
    if request.method == 'GET' :
        return render_template('admn_login.html')
    if request.method == 'POST' :
        return render_template('user_dashboard.html')