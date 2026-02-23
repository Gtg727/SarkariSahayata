import functools
import time
import random
import re

from flask import (
    Blueprint, flash, g, redirect,
    render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db
from flaskr import email, mail, limiter


bp = Blueprint('auth', __name__, url_prefix='/auth')


# ---------------- PASSWORD VALIDATION ----------------

def validate_password(password, username):

    if len(password) < 8:
        return "Password must be at least 8 characters long."

    if re.search(r"\s", password):
        return "Password must not contain spaces."

    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter."

    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter."

    if not re.search(r"[0-9]", password):
        return "Password must contain at least one number."

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must contain at least one special character."

    if password.lower() == username.lower():
        return "Password cannot be same as username."

    return None


# ---------------- OTP CREATION ----------------

def create_otp(id):
    db = get_db()
    cur = db.cursor()

    otp = str(random.randint(100000, 999999))

    try:
        cur.execute(
            "INSERT INTO otps (id, otp, created) VALUES (%s, %s, %s)",
            (id, otp, time.time()),
        )
    except:
        cur.execute("DELETE FROM otps WHERE id=%s", (id,))
        db.commit()
        cur.execute(
            "INSERT INTO otps (id, otp, created) VALUES (%s, %s, %s)",
            (id, otp, time.time()),
        )

    db.commit()

    cur.execute(
        "INSERT INTO otps (id, otp, created) VALUES (%s, %s, %s)",
        (user_id, otp, time.time()),
    )
    db.commit()

    return otp


# =========================================
# REGISTER
# =========================================
@bp.route('/register', methods=('GET', 'POST'))
@limiter.limit("5 per minute")
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        emails = request.form['email']

        db = get_db()
        cur = db.cursor()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        else:
            error = validate_password(password, username)

        if error is None:
            try:
                cur.execute(
                    "INSERT INTO user (username, email, password, is_registered) VALUES (%s, %s, %s, 0)",
                    (username, emails, generate_password_hash(password)),
                )
                db.commit()

                cur.execute("SELECT * FROM user WHERE username = %s", (username,))
                user = cur.fetchone()

                otp = create_otp(user['id'])

            except Exception:
                error = f"User {username} is already registered."
            else:
                html = render_template('auth/confirmation_mail.html', otp=otp)
                email.send_email(
                    user['email'],
                    "Otp to verify registration",
                    html,
                    mail
                )
                return redirect(url_for("auth.verify_otp", email_s=user['email']))

        flash(error)

    return render_template('auth/register.html')


# =========================================
# LOGIN
# =========================================
@bp.route('/login', methods=('GET', 'POST'))
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        cur = db.cursor()

        error = None

        cur.execute("SELECT * FROM user WHERE username = %s", (username,))
        user = cur.fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        elif user['is_registered'] == 0:
            error = 'Email not verified. Please complete registration.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('home.index'))   # ✅ FIXED

        flash(error)

    return render_template('auth/login.html')


# =========================================
# LOAD USER
# =========================================
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    db = get_db()
    cur = db.cursor()

    if user_id is None:
        g.user = None
    else:
        cur.execute("SELECT * FROM user WHERE id = %s", (user_id,))
        g.user = cur.fetchone()


# =========================================
# LOGOUT
# =========================================
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home.index'))   # ✅ FIXED


# =========================================
# VERIFY OTP
# =========================================
@bp.route('/verify-otp/<email_s>', methods=('GET', 'POST'))
@limiter.limit("5 per minute")
def verify_otp(email_s):

    duration = 600  # 10 minutes

    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT * FROM user WHERE email=%s", (email_s,))
    user = cur.fetchone()

    if not user:
        flash("Invalid email.")
        return redirect(url_for("auth.register"))

    cur.execute("SELECT * FROM otps WHERE id=%s", (user['id'],))
    record = cur.fetchone()

    if request.method == 'POST':
        otp = request.form['otp']

        if record and record['otp'] == otp and (time.time() - record['created'] < duration):

            cur.execute(
                "UPDATE user SET is_registered = 1 WHERE id=%s",
                (user['id'],)
            )
            db.commit()

            flash("Email verified successfully. Please login.")
            return redirect(url_for('auth.login'))   # ✅ FIXED

        else:
            flash("Invalid or expired OTP.")

    return render_template('auth/verify_otp.html')


# =========================================
# LOGIN REQUIRED DECORATOR
# =========================================
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view
