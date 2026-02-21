from flask import (
    Blueprint, flash, g, redirect,
    render_template, request, url_for, abort
)
from flaskr.db import get_db
import MySQLdb.cursors


# =====================================================
# Blueprint
# =====================================================
bp = Blueprint('home', __name__)


# =====================================================
# HOME PAGE
# =====================================================
@bp.route("/")
def index():

    db = get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("SELECT * FROM schemes ORDER BY id DESC")
    schemes = cursor.fetchall()

    return render_template("index.html", schemes=schemes)


# =====================================================
# SCHEME DETAIL PAGE
# =====================================================
@bp.route('/scheme/<int:scheme_id>')
def scheme_detail(scheme_id):

    db = get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("SELECT * FROM schemes WHERE id=%s", (scheme_id,))
    scheme = cursor.fetchone()

    if not scheme:
        abort(404)

    return render_template("scheme_detail.html", scheme=scheme)


# =====================================================
# ADD USER DETAILS
# =====================================================
@bp.route("/add-details", methods=["GET", "POST"])
def add_details():

    if not g.user:
        return redirect(url_for("auth.login"))

    db = get_db()
    cursor = db.cursor()

    if request.method == "POST":

        name = request.form.get("name")
        age = request.form.get("age")
        gender = request.form.get("gender")
        income = request.form.get("income")
        caste = request.form.get("caste")
        state = request.form.get("state")
        occupation = request.form.get("occupation")
        aadhar = request.form.get("aadhar")
        pan = request.form.get("pan")

        cursor.execute("""
            INSERT INTO user_details
            (name, age, gender, income, caste, states,
             occupation, aadhar, pan, user_id)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            name, age, gender, income, caste,
            state, occupation, aadhar, pan, g.user["id"]
        ))

        db.commit()
        flash("User details submitted successfully!")

        return redirect(url_for("home.index"))

    return render_template("add_details.html")


# =====================================================
# ELIGIBILITY ENGINE (FULLY DATABASE DRIVEN)
# =====================================================
@bp.route("/eligibility")
def eligibility():

    if not g.user:
        return redirect(url_for("auth.login"))

    db = get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    # Get user details
    cursor.execute("""
        SELECT * FROM user_details
        WHERE user_id = %s
    """, (g.user["id"],))

    user = cursor.fetchone()

    if not user:
        flash("Please add your details first.")
        return redirect(url_for("home.add_details"))

    age = int(user["age"] or 0)
    gender = (user["gender"] or "").lower()
    income = int(user["income"] or 0)
    caste = (user["caste"] or "").lower()
    state = (user["states"] or "").lower()
    occupation = (user["occupation"] or "").lower()

    # Get all schemes
    cursor.execute("SELECT * FROM schemes")
    schemes = cursor.fetchall()

    eligible_schemes = []
    rejected_schemes = []

    for scheme in schemes:

        is_eligible = True
        reasons = []

        # ---------------- AGE CHECK ----------------
        if scheme["min_age"] and age < scheme["min_age"]:
            is_eligible = False
            reasons.append(f"Minimum age required is {scheme['min_age']}")

        if scheme["max_age"] and age > scheme["max_age"]:
            is_eligible = False
            reasons.append(f"Maximum age allowed is {scheme['max_age']}")

        # ---------------- INCOME CHECK ----------------
        if scheme["max_income"] and income > scheme["max_income"]:
            is_eligible = False
            reasons.append(f"Income must be ≤ ₹{scheme['max_income']}")

        # ---------------- GENDER CHECK ----------------
        if scheme["gender"] and scheme["gender"].lower() != gender:
            is_eligible = False
            reasons.append(f"Only for {scheme['gender']} candidates")

        # ---------------- CASTE CHECK ----------------
        if scheme["caste"] and scheme["caste"].lower() != caste:
            is_eligible = False
            reasons.append(f"Only for {scheme['caste']} category")

        # ---------------- STATE CHECK ----------------
        if scheme["state"] and scheme["state"].lower() != state:
            is_eligible = False
            reasons.append(f"Only available in {scheme['state']}")

        # ---------------- OCCUPATION CHECK ----------------
        if scheme["occupation"] and scheme["occupation"].lower() != occupation:
            is_eligible = False
            reasons.append(f"Only for {scheme['occupation']} occupation")

        # ---------------- FINAL RESULT ----------------
        if is_eligible:
            eligible_schemes.append({
                "scheme": scheme,
                "reason": "All eligibility criteria satisfied"
            })
        else:
            rejected_schemes.append({
                "scheme": scheme,
                "reasons": reasons
            })

    return render_template(
        "eligibility.html",
        name=user["name"],
        eligible_schemes=eligible_schemes,
        rejected_schemes=rejected_schemes,
        scheme_count=len(eligible_schemes)
    )