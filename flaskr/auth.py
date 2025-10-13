import functools
import time
import random

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

from flaskr import email, mail

bp = Blueprint('auth', __name__, url_prefix='/auth')

def create_otp(id):
    db = get_db()

    otp = str(random.randint(100000, 999999))

    try:
        db.execute(
            "INSERT INTO otps (id, otp, created) VALUES (?, ?, ?)",
            (id,otp,time.time()),
        )
    except:
        db.execute(
            "DELETE FROM otps Where id=?",(id,),
        )
        db.commit()
        db.execute(
            "INSERT INTO otps (id, otp, created) VALUES (?, ?, ?)",
            (id,otp,time.time()),
        )

    db.commit()
    return otp

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        emails = request.form['email']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, email, password) VALUES (?, ?, ?)",
                    (username, emails, generate_password_hash(password)),
                )
                db.commit()

                user = db.execute(
                    'SELECT * FROM user WHERE username = ?', (username,)
                ).fetchone()

                otp = create_otp(user['id'])
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                html = render_template('auth/confirmation_mail.html',otp=otp)
                email.send_email(user['email'],"Otp to verify registration",html,mail)
                return redirect(url_for("auth.verify_otp",email_s=user['email']))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        elif user['is_registered'] == 0:
            error = 'email not verified , repeat registration process again'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('static',filename="auth/login_success.html"))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@bp.route('/verify-otp/<email_s>', methods=('GET', 'POST'))
def verify_otp(email_s):
    duration = 600
    db = get_db()
    user = db.execute("SELECT * FROM user WHERE email=?", (email_s,)).fetchone()

    if not user:
        flash("Invalid email for verification.")
        return redirect(url_for("auth.register"))
    
    record = db.execute("SELECT * FROM otps WHERE id=?", (user['id'],)).fetchone()
    
    if request.method == 'POST':
        otp = request.form['otp']
        if record['otp'] == otp and (time.time() - record['created'] < duration):
            if user['is_registered']:
                return redirect(url_for("static",filename="auth/login_success.html"))
            else:
                db.execute(
                    "UPDATE user SET is_registered = TRUE WHERE id=?", (user['id'],)
                )
                db.commit()
                #return redirect(url_for("static",filename="auth/registration_success.html"))
                return redirect(url_for('static',filename="auth/login_success.html"))
        else:
            if record['otp'] != otp:
                flash("Wrong otp")
            
    return render_template('auth/verify_otp.html')

def login_required(f):
    @functools.wraps(f)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return f(**kwargs)

    return wrapped_view