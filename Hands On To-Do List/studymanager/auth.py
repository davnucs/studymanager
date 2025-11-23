from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from . import app, db
from .models import User
import logging

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if not username or not password:
            flash('Username and password are required.')
            return render_template('login.html')
        try:
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('boards'))
            else:
                flash('Invalid username or password.')
        except Exception as e:
            logging.error(f"Login error: {str(e)}")
            db.session.rollback()
            flash('An error occurred during login. Please try again.')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        if not username or not password or not confirm_password:
            flash('All fields are required.')
            return render_template('register.html')
        if password != confirm_password:
            flash('Passwords do not match.')
            return render_template('register.html')
        if len(password) < 6:
            flash('Password must be at least 6 characters long.')
            return render_template('register.html')
        try:
            if User.query.filter_by(username=username).first():
                flash('Username already exists.')
                return render_template('register.html')
            user = User(username=username, password=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('boards'))
        except Exception as e:
            logging.error(f"Registration error: {str(e)}")
            db.session.rollback()
            flash('An error occurred during registration. Please try again.')
    return render_template('register.html')

@app.route('/logout')
def logout():
    logout_user()
    from flask import get_flashed_messages
    get_flashed_messages()  # Consumes the messages
    return redirect(url_for('login'))