from forms import LoginForm, RegisterForm, GroupForm, JoinForm
from email.policy import default
from flask import Flask, render_template, abort, request, session
from flask_sqlalchemy import SQLAlchemy
from flask import session, redirect, url_for
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
import random
import string
import datetime
import os

app = Flask(__name__,template_folder='templates')

UPLOAD_FOLDER = 'static/images/users/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['SECRET_KEY'] = 'dfewfew123213rwdsgert34tgfd1234trgf'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(60), nullable=False)

class Group(db.Model):
    group_id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(20), nullable=False)
    budget = db.Column(db.String(20), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(20), nullable=False)
    group_pic = db.Column(db.String(120), nullable=False)
    group_members = db.relationship('User', secondary='group_members', backref=db.backref('groups', lazy=True))
    join_code = db.Column(db.String(20), nullable=False)

class GroupMembers(db.Model):
    group_member_id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.group_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

db.create_all()

@app.route('/home', methods=['GET', 'POST'])
def home():
    group_form = GroupForm()
    join_form = JoinForm()

    if group_form.validate_on_submit():
        if group_form.group_pic.data != None:
            group_id = Group.query.count() + 1
            group_name = group_form.group_name.data
            budget = group_form.budget.data
            date = group_form.date.data
            date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
            location = group_form.location.data
            group_pic = group_form.group_pic.data
            filename = secure_filename(group_pic.filename)
            group_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            join_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            group = Group(group_id=group_id, group_name=group_name, budget=budget, date=date, location=location, group_pic=filename, join_code=join_code)
            group.group_members.append(User.query.filter_by(user_id=session['user_id']).first())
            db.session.add(group)
            db.session.commit()
            return redirect(url_for('home'))

    if join_form.validate_on_submit():
        join_code = join_form.join_code.data
        group = Group.query.filter_by(join_code=join_code).first()
        if group != None:
            group.group_members.append(User.query.filter_by(user_id=session['user_id']).first())
            db.session.commit()
            groups = Group.query.filter(Group.group_members.any(user_id=session['user_id'])).all()
            return render_template('home.html', user = session['user'], join_form=join_form, group_form=group_form, groups=groups)
        else:
            return render_template('home.html', group_form=group_form, join_form=join_form, error='Invalid join code')

    if 'user' in session:
        groups = Group.query.filter(Group.group_members.any(user_id=session['user_id'])).all()
        return render_template('home.html', user = session['user'], group_form = group_form, groups = groups, join_form = join_form)

    else:
        return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                session['user'] = user.full_name
                session['user_id'] = user.user_id
                return redirect(url_for('home'))
            else:
                return render_template('login.html', form=form, error='Wrong password')
        else:
            return render_template('login.html', form=form, error='User not found')
    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user_id = User.query.count() + 1
            full_name = form.full_name.data
            email = form.email.data
            password = form.password.data
            hashed_password = bcrypt.generate_password_hash(password=password).decode('utf-8')
            if User.query.filter_by(email=email).first():
                return render_template('signup.html', form=form, error='Email already exists')
            new_user = User(user_id=user_id, full_name=full_name, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        else:
            return render_template('signup.html', form=form)
    return render_template('signup.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(port=3000, debug=True)