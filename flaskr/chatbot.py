import re
from flask import Blueprint, render_template, request, jsonify, session
from flaskr.db import get_db
import MySQLdb.cursors

bp = Blueprint("chatbot", __name__, url_prefix="/chatbot")


# ==========================================
# CHATBOT PAGE
# ==========================================
@bp.route("/")
def chatbot_page():
    return render_template("chatbot.html")


# ==========================================
# MAIN CHAT API
# ==========================================
@bp.route("/api", methods=["POST"])
def chat_api():

    data = request.get_json()
    message = data.get("message", "").strip().lower()

    db = get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    # ==========================================================
    # 1️⃣ CATEGORY SEARCH + COUNT
    # ==========================================================
    category_match = re.search(
        r"(agriculture|education|health|housing|skills|transport|women)",
        message
    )

    if category_match and "scheme" in message:
        category = category_match.group(1)

        cursor.execute("""
            SELECT title FROM schemes
            WHERE LOWER(category) LIKE %s
        """, (f"%{category}%",))

        schemes = cursor.fetchall()

        if not schemes:
            return jsonify({"reply": "No schemes found in this category."})

        # Count Query
        if "how many" in message:
            return jsonify({
                "reply": f"There are <b>{len(schemes)}</b> schemes under <b>{category.title()}</b>."
            })

        # List Query
        reply = f"<b>{category.title()} Schemes:</b><br><br>"
        for scheme in schemes:
            reply += f"• {scheme['title']}<br>"

        return jsonify({"reply": reply})


    # ==========================================================
    # 2️⃣ DOCUMENT QUERY
    # Example: "documents required for demo scheme"
    # ==========================================================
    if "document" in message:

        cursor.execute("SELECT title, documents FROM schemes")
        schemes = cursor.fetchall()

        for scheme in schemes:
            if scheme["title"].lower() in message:
                if scheme["documents"]:
                    formatted = scheme["documents"].replace("\n", "<br>")
                    return jsonify({
                        "reply": f"<b>Documents Required for {scheme['title']}:</b><br><br>{formatted}"
                    })
                else:
                    return jsonify({
                        "reply": f"No document information available for {scheme['title']}."
                    })


    # ==========================================================
    # 3️⃣ BENEFITS QUERY
    # ==========================================================
    if "benefit" in message:

        cursor.execute("SELECT title, benefits FROM schemes")
        schemes = cursor.fetchall()

        for scheme in schemes:
            if scheme["title"].lower() in message:
                if scheme["benefits"]:
                    formatted = scheme["benefits"].replace("\n", "<br>")
                    return jsonify({
                        "reply": f"<b>Benefits of {scheme['title']}:</b><br><br>{formatted}"
                    })
                else:
                    return jsonify({
                        "reply": f"No benefit information available for {scheme['title']}."
                    })


    # ==========================================================
    # 4️⃣ ELIGIBILITY FLOW START
    # ==========================================================
    if "check eligibility" in message:
        session["chat_state"] = "ask_age"
        session["eligibility_data"] = {}
        return jsonify({"reply": "Please enter your age."})


    # ==========================================================
    # ELIGIBILITY STEP 1 — AGE
    # ==========================================================
    if session.get("chat_state") == "ask_age":

        if not message.isdigit():
            return jsonify({"reply": "Please enter your age in numbers only."})

        session["eligibility_data"]["age"] = int(message)
        session["chat_state"] = "ask_income"

        return jsonify({"reply": "Please enter your annual income."})


    # ==========================================================
    # ELIGIBILITY STEP 2 — INCOME
    # ==========================================================
    if session.get("chat_state") == "ask_income":

        if not message.isdigit():
            return jsonify({"reply": "Please enter your income in numbers only."})

        session["eligibility_data"]["income"] = int(message)
        session["chat_state"] = None

        age = session["eligibility_data"]["age"]
        income = session["eligibility_data"]["income"]

        cursor.execute("""
            SELECT title FROM schemes
            WHERE (min_age IS NULL OR min_age <= %s)
            AND (max_age IS NULL OR max_age >= %s)
            AND (max_income IS NULL OR max_income >= %s)
        """, (age, age, income))

        eligible = cursor.fetchall()

        if eligible:
            reply = "<b>You are eligible for:</b><br><br>"
            for scheme in eligible:
                reply += f"• {scheme['title']}<br>"
        else:
            reply = "No schemes matched your eligibility criteria."

        return jsonify({"reply": reply})


    # ==========================================================
    # STRICT DEFAULT RESPONSE
    # ==========================================================
    return jsonify({
        "reply": """
I can only help with:

• Category based scheme search  
• Documents required for a scheme  
• Benefits of a scheme  
• Eligibility check  

Please ask a valid supported question.
"""
    })


# ==========================================
# LIVE QUESTION SUGGESTIONS (DATABASE DRIVEN)
# ==========================================
@bp.route("/suggest", methods=["POST"])
def suggest():

    data = request.get_json()
    user_input = data.get("text", "").lower().strip()

    if not user_input:
        return jsonify({"suggestions": []})

    db = get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("SELECT title, category FROM schemes")
    schemes = cursor.fetchall()

    suggestions = []

    # Category based suggestions
    categories = set([s["category"].lower() for s in schemes if s["category"]])

    for category in categories:
        possible = [
            f"Show {category} schemes",
            f"How many {category} schemes are there?"
        ]
        for q in possible:
            if user_input in q.lower():
                suggestions.append(q)

    # Scheme based suggestions
    for scheme in schemes:
        title = scheme["title"]

        possible = [
            f"What documents are required for {title}?",
            f"What are the benefits of {title}?",
            f"Check eligibility for {title}"
        ]

        for q in possible:
            if user_input in q.lower():
                suggestions.append(q)

    return jsonify({"suggestions": suggestions[:6]})