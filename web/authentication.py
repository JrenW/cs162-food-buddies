from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db,User
from . import login_manager
from flask import current_app as app

authentication = Blueprint("authentication",__name__)

# routes on user management
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@authentication.route('/sign_up', methods=['GET','POST'])
def sign_up():
    # when button to sign up on login page is clicked
    if request.method == 'GET':
        return render_template('signUp.html')
    elif request.method == 'POST':
        # check that email is not already registered
        email = str(request.form['email']).lower()
        user = db.session.query(User).filter(User.email==email).first()
        city_selected = request.form.get('city_selected')
        if not user: # create a new user profile
            hashed_pwd = generate_password_hash(request.form['password'], method='sha256')
            #request.form['contact_info'] -- For getting the contact info!
            #request.form['contact_method'] -- For getting the contact method
            user = User(first_name=request.form['first_name'],last_name=request.form['last_name'], email=email,password=hashed_pwd, city=str(city_selected))
            db.session.add(user)
            db.session.commit()

            #Login the user after signup
            logged_user = User.query.filter_by(email=email).first()
            login_user(logged_user, remember=False)
            return redirect(url_for('main_route.preference'))
        else:
            flash('This email already has an account.')
            return render_template('signUp.html')

# route will depend on whether how we structure pages
# is index the login + homepage or the page selecting preferences to then be matched?
@authentication.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        email = str(request.form['email']).lower()
        user = db.session.query(User).filter(User.email == email).first()
        # check that the user is in the database
        if user:
            if check_password_hash(user.password, request.form['password']):
                login_user(user)
                # return redirect(url_for('index'))
                return redirect(url_for('main_route.preference'))
            else:
                flash('Incorrect Password!', "error")
                return redirect(url_for('authentication.login'))
        else:
            flash('This email does not have an account.', "error")
            return redirect(url_for('authentication.login'))

@authentication.route('/logout')
@login_required
def log_out():
    logout_user()
    return redirect(url_for(('main_route.index')))


@authentication.route('/verifyEmail', methods=['POST'])
def verifyEmail():
    email = str(request.form['verEmail']).lower()
    user = db.session.query(User).filter(User.email == email).first()
    # check that the user is in the database
    if user:
        flash('An email sent to you for resetting your password!', 'inform')
        
        #Send an Email here with the token!

        return redirect(url_for('authentication.login'))
    else:
        flash('This email does not have an account.', "error")
        return redirect(url_for('authentication.login'))
