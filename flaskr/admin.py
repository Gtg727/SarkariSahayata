from flask import Blueprint, render_template, request, redirect, url_for, session
import json
import os

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

ADMIN_USERNAME = "sarkariadmin1"
ADMIN_PASSWORD = "sarkari123"

DATA_FILE = os.path.join("data", "schemes.json")

# ---------------- ADMIN LOGIN ----------------
@admin_bp.route("/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin.admin_dashboard"))

    return render_template("admin_login.html")


# ---------------- ADMIN DASHBOARD ----------------
@admin_bp.route("/dashboard", methods=["GET", "POST"])
def admin_dashboard():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.admin_login"))

    if request.method == "POST":
        scheme = {
            "title": request.form.get("title"),
            "category": request.form.get("category"),
            "description": request.form.get("description"),
            "benefits": request.form.get("benefits"),
            "eligibility": request.form.get("eligibility")
        }

        with open(DATA_FILE, "r") as f:
            data = json.load(f)

        data.append(scheme)

        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)

    return render_template("admin_dashboard.html")


# ---------------- LOGOUT ----------------
@admin_bp.route("/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin.admin_login"))
