from flask import request, Flask, flash
from flask import render_template, url_for, redirect
from flask import current_app as app 
from application.models import *
from flask_basicauth import BasicAuth



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
       
        #email=request.form.get("email"),
        #print(db.session.query(User).filter_by(email=email).first())
        #if (email == db.session.query(User).filter_by(email=email).first().email):
            #db.session.close()
            #return render_template('registration_except.html')
    try:
        password =request.form["password"]
        confirmpassword =request.form["confirmpassword"]
        if (password==confirmpassword):
            db.session.add(user)
            db.session.commit()
            db.session.close()
            flash('You were successfully Registered, now login')
            return redirect(url_for("user_login"))
        
        else :
             return render_template('passwordvalidation.html')
        
    except:
        return render_template('registration_except.html')







@app.route("/user_login", methods = ['GET', 'POST'])
def user_login():
    if request.method == 'GET' :
        return render_template('usr_login.html')
    if request.method == 'POST' :
        email = request.form.get("email")
        user = db.session.query(User).filter_by(email=email).first()
        if user and (user.password == request.form.get("password")) : 
            app.logger.info(f"Login successful for {email}")
            return render_template('user_dashboard.html', email=email)
        else:
            flash('Invalid email or password. Please try again.')
            app.logger.warning(f"Login failed for {email}")
            return redirect(url_for("user_login"))






basic_auth = BasicAuth(app)
@app.route("/admin", methods = ['GET', 'POST'])
@basic_auth.required
def admin_login():
    if request.method == 'GET' :
        return render_template('admn_login.html')
    if request.method == 'POST' :
        uname = request.form.get("username")
        pwd = request.form.get("password")
        print(request.form)
        if uname == 'virat'  and pwd == 'jain' : 
            app.logger.info(f"Login successful for {uname}")
            return render_template('user_dashboard.html', email='ADMIN PAGE')
        else:
            flash('Invalid email or password. Please try again.')
            app.logger.warning(f"Login failed")
            return redirect(url_for("user_login"))
    