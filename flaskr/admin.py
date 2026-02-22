from flask import Blueprint, render_template, request, redirect, url_for, session
from flaskr.db import get_db
import MySQLdb.cursors

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# =========================
# ADMIN LOGIN
# # =========================
# @admin_bp.route("/login", methods=["GET", "POST"])
# def admin_login():

#     if request.method == "POST":
#         username = request.form.get("username")
#         password = request.form.get("password")

#         if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
#             session["admin_logged_in"] = True
#             return redirect(url_for("admin.admin_dashboard"))

#     return render_template("admin_login.html")


# =========================
# ADMIN DASHBOARD
# =========================
@admin_bp.route("/admin_page", methods=["GET", "POST"])
def admin_dashboard():

    #if not session.get("admin_logged_in"):
    #    return redirect(url_for("admin.admin_login"))

    db = get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    if request.method == "POST":

        # ------------------------
        # BASIC INFO
        # ------------------------
        title = request.form.get("title")
        category = request.form.get("category")
        description = request.form.get("description") or None
        benefits = request.form.get("benefits") or None
        objectives = request.form.get("objectives") or None
        application_process = request.form.get("application_process") or None
        documents = request.form.get("documents") or None

        # ------------------------
        # ELIGIBILITY
        # ------------------------
        min_age = request.form.get("min_age")
        min_age = int(min_age) if min_age else None

        max_age = request.form.get("max_age")
        max_age = int(max_age) if max_age else None

        max_income = request.form.get("max_income")
        max_income = int(max_income) if max_income else None

        gender = request.form.get("gender") or None
        caste = request.form.get("caste") or None
        state = request.form.get("state") or None
        occupation = request.form.get("occupation") or None

        # ------------------------
        # INSERT INTO DATABASE
        # ------------------------
        cursor.execute("""
            INSERT INTO schemes
            (title, category, description, benefits, objectives,
             application_process, documents,
             min_age, max_age, max_income,
             gender, caste, state, occupation)
            VALUES (%s, %s, %s, %s, %s,
                    %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s)
        """, (
            title, category, description, benefits, objectives,
            application_process, documents,
            min_age, max_age, max_income,
            gender, caste, state, occupation
        ))

        db.commit()

        return redirect(url_for("admin.admin_dashboard"))

    # Fetch all schemes
    cursor.execute("SELECT * FROM schemes ORDER BY id DESC")
    schemes = cursor.fetchall()

    return render_template("admin_dashboard.html", schemes=schemes)

# =========================
# LOGOUT
# =========================
# @admin_bp.route("/logout")
# def admin_logout():
#     session.pop("admin_logged_in", None)
#     return redirect(url_for("admin.admin_login"))