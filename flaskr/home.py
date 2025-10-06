import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.db import get_db

bp = Blueprint('home', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/add-details', methods=['GET', 'POST'])
# @login_required
def add_details():
    db = get_db()

    if request.method == 'POST':
        # Fetch form data
        name = request.form.get('name')
        age = request.form.get('age')
        gender = request.form.get('gender')
        income = request.form.get('income')
        caste = request.form.get('caste')
        state = request.form.get('state')
        occupation = request.form.get('occupation')
        aadhar = request.form.get('aadhar')
        pan = request.form.get('pan')

        # Insert user details
        db.execute(
            "INSERT INTO user_details (name, age, gender, income, caste, states, occupation, aadhar, pan, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        , (name, age, gender, income, caste, state, occupation, aadhar, pan, g.user['id'])),
        db.commit()

        flash("User details submitted successfully!")
        g.details = True
        return redirect(url_for('home.index'))

    return render_template('add_details.html')

@bp.route('/eligibility')
# @login_required
def eligibility():
    """Check eligible schemes based on user details."""
    print("hello")
    db = get_db()
    user = db.execute("SELECT * FROM user_details WHERE user_id=?", (g.user['id'],)).fetchone()

    if not user:
        flash("Please add your details first.")
        return redirect(url_for('home.add_details'))

    # Extract user data
    age = int(user['age'] or 0)
    gender = (user['gender'] or "").lower()
    income = int(user['income'] or 0)
    caste = (user['caste'] or "").lower()
    occupation = (user['occupation'] or "").lower()

    # Eligibility logic
    schemes = {
        "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)": occupation == "farmer" and income <= 120000,
        "Pradhan Mantri Adarsh Gram Yojana (PMAGY)": caste == "sc",
        "Prime Minister’s Fellowship for Doctoral Research": age <= 42,
        "Prime Minister Early Career Research Grant (PM ECRG)": age <= 42 and caste in ["sc", "st", "obc"] and gender == "female",
        "Ayushman Bharat Pradhan Mantri Jan Arogya Yojana (AB-PMJAY)": income <= 120000,
        "Pradhan Mantri Bhartiya Janaushadhi Pariyojana (PMBJP)": caste in ["sc", "st"] and gender == "female" and occupation == "divyang",
        "Pradhan Mantri Awaas Yojana Gramin (PMAY-G)": income <= 10000 and caste in ["sc", "st"] and occupation == "pwd",
        "Pradhan Mantri Awas Yojana Urban (PMAY-U, CLSS)": income <= 1800000,
        "Pradhan Mantri Kaushal Vikas Yojana Short Term Training (PMKVY-STT)": 15 <= age <= 45,
        "Prime Minister’s Employment Generation Programme (PMEGP)": age >= 18,
        "Mahila Samman Savings Certificate (MSSC)": gender == "female",
        "Transport Allowance to Differently Abled Persons (Puducherry)": age >= 5 and income <= 75000,
        "Scheme for Financial Assistance for Veteran Artists (Artists’ Pension)": age >= 60 and income <= 48000
    }

    eligible_schemes = [s for s, cond in schemes.items() if cond]

    return render_template(
        "eligibility.html",
        name=user['name'],
        eligible_schemes=eligible_schemes,
        scheme_count=len(eligible_schemes)
    )
