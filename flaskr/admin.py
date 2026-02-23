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

@admin_bp.route("/dashboard")
def info_dashboard():
    db = get_db()
    cur = db.cursor()

    gender = []

    try:
        cur.execute("select count(*) from user_details where gender = %s",('Male',))
        male = cur.fetchone()
        gender.append(male['count(*)'])
    except:
        male = 0
        gender.append(male)
  
    try:
        print("yay")
        cur.execute("select count(*) from user_details where gender = %s",('Female',))
        female = cur.fetchone()
        gender.append(female['count(*)'])
    except:
        female = 0
        gender.append(female)
    
    cur.execute("select count(*) from user")
    registered_no = cur.fetchone()
    cur.execute("select count(*) from user_details")
    info_no = cur.fetchone()
    cur.execute("select count(*) from schemes")
    total_schemes = cur.fetchone()
    
    categories = ['Education', 'Health', 'Agriculture', 'Skills and Employment', 'Housing', 'Women and Child']
    cat_count = []

    for c in categories:
        cur.execute("select count(*) from schemes where category = %s",(c,))
        temp = cur.fetchone()
        cat_count.append(temp['count(*)'])

    cur.close()

    return render_template("admin/dashboard.html", 
                           gender_data=gender,
                           registrations=registered_no['count(*)'],
                           info=info_no['count(*)'],
                           total_schemes=total_schemes['count(*)'],
                           cat_list=cat_count
                           )

@admin_bp.route("/view_user", methods=['GET', 'POST'])
def view_user():
    db = get_db()
    cur = db.cursor()

    # if request.method =='POST':
    #     name = request.args.get("name")
    #     print(name)

    #     cur.execute("select user_type from user where username = %s",(name,))
    #     types = cur.fetchone()

    #     if types['user_type'] == 'user':
    #         cur.execute("UPDATE user set user_type = %s where username = %s",('admin',name,))
    #     elif types['user_type'] == 'admin':
    #         cur.execute("UPDATE user set user_type = %s where username = %s",('user',name,))

    #     cur.commit()

    cur.execute("select * from user")

    users = cur.fetchall()

    return render_template("admin/view_users.html",users=users)
# =========================
# LOGOUT
# =========================
# @admin_bp.route("/logout")
# def admin_logout():
#     session.pop("admin_logged_in", None)
#     return redirect(url_for("admin.admin_login"))