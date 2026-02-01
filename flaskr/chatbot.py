from flask import Blueprint, render_template, request, jsonify, session

# -----------------------------------
# Blueprint Setup
# -----------------------------------
bp = Blueprint("chatbot", __name__, url_prefix="/chatbot")

# -----------------------------------
# Scheme Database (Dummy Data)
# -----------------------------------
SCHEMES = {
    "women": [
        "Beti Bachao Beti Padhao",
        "Sukanya Samriddhi Yojana",
        "Mahila Samman Savings Certificate",
        "Working Women Hostel Scheme",
        "Pradhan Mantri Ujjwala Yojana",
        "AICTE Pragati Scholarship for Girls"
    ],
    "student": [
        "National Scholarship Portal (NSP)",
        "Post Matric Scholarship for SC/ST/OBC",
        "PM Vidya Lakshmi Education Loan",
        "AICTE Saksham Scholarship",
        "Central Sector Scholarship Scheme"
    ],
    "farmer": [
        "PM-KISAN Samman Nidhi",
        "PM Fasal Bima Yojana",
        "Kisan Credit Card (KCC)",
        "Soil Health Card Scheme",
        "National Agriculture Market (e-NAM)"
    ],
    "health": [
        "Ayushman Bharat Yojana",
        "Janani Suraksha Yojana",
        "PM Jan Arogya Yojana",
        "National Health Mission",
        "Pradhan Mantri Bhartiya Janaushadhi Pariyojana"
    ]
}

# -----------------------------------
# Chatbot UI Page
# -----------------------------------
@bp.route("/", endpoint="chatbot_page")
def chatbot_page():
    return render_template("chatbot.html")

# -----------------------------------
# Chatbot API
# -----------------------------------
@bp.route("/api", methods=["POST"])
def chat_api():
    data = request.get_json(silent=True)

    if not data or "message" not in data:
        return jsonify({"reply": "Please type a message to continue."})

    msg = data["message"].lower().strip()

    # -----------------------------------
    # Reset Command
    # -----------------------------------
    if msg == "reset":
        session.pop("intent", None)
        session.pop("age", None)
        session.pop("occupation", None)

        return jsonify({
            "reply": (
                "🔄 All details cleared!\n\n"
                "You can ask for:\n"
                "• Women schemes\n"
                "• Student schemes\n"
                "• Farmer schemes\n"
                "• Health schemes\n\n"
                "Or type: check eligibility"
            )
        })

    # -----------------------------------
    # Greeting
    # -----------------------------------
    if msg in ["hi", "hello", "hey"]:
        return jsonify({
            "reply": (
                "Hello! 👋 I’m your SarkariSahayata AI Assistant.\n\n"
                "You can ask for:\n"
                "• Women schemes\n"
                "• Student schemes\n"
                "• Farmer schemes\n"
                "• Health schemes\n\n"
                "Or type: check eligibility"
            )
        })

    # -----------------------------------
    # Detect Scheme Type
    # -----------------------------------
    for key in SCHEMES.keys():
        if key in msg:
            session["intent"] = key

            schemes = SCHEMES[key]
            scheme_text = "\n\n".join([f"• {s}" for s in schemes])

            return jsonify({
                "reply": (
                    f"📌 {key.capitalize()} Related Government Schemes\n\n"
                    f"{scheme_text}\n\n"
                    "🔍 Want personalized eligibility?\n"
                    "Type: check eligibility"
                )
            })

    # -----------------------------------
    # Eligibility Flow
    # -----------------------------------
    if msg == "check eligibility":
        if "age" not in session:
            return jsonify({"reply": "Please tell me your age."})
        if "occupation" not in session:
            return jsonify({"reply": "Please tell me your occupation."})

        return show_eligibility()

    # -----------------------------------
    # Capture Age
    # -----------------------------------
    if msg.isdigit():
        session["age"] = int(msg)
        return jsonify({"reply": "Got it! Now tell me your occupation (student, farmer, worker, etc.)."})

    # -----------------------------------
    # Capture Occupation
    # -----------------------------------
    if "age" in session and "occupation" not in session:
        session["occupation"] = msg
        return show_eligibility()

    # -----------------------------------
    # Fallback
    # -----------------------------------
    return jsonify({
        "reply": (
            "🤖 I didn’t fully understand that.\n\n"
            "Try typing:\n"
            "• Women schemes\n"
            "• Student schemes\n"
            "• Farmer schemes\n"
            "• Health schemes\n"
            "• check eligibility\n"
            "• reset"
        )
    })

# -----------------------------------
# Eligibility Output Formatter
# -----------------------------------
def show_eligibility():
    intent = session.get("intent", "schemes")
    age = session.get("age", "Not provided")
    occupation = session.get("occupation", "Not provided")

    schemes = SCHEMES.get(intent, [])
    scheme_text = "\n\n".join([f"• {s}" for s in schemes])

    return jsonify({
        "reply": (
            "🧾 Your Profile Summary\n\n"
            f"• Age: {age}\n"
            f"• Occupation: {occupation}\n\n"
            "🎯 Eligible Government Schemes\n\n"
            f"{scheme_text}\n\n"
            "🔄 To start a new search, type: reset"
        )
    })
