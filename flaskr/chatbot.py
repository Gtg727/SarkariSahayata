from flask import Blueprint, render_template, request, jsonify, session

bp = Blueprint("chatbot", __name__, url_prefix="/chatbot")

# -----------------------------------
# Dummy Scheme Database
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
# UI Page
# -----------------------------------
@bp.route("/")
def chatbot_page():
    return render_template("chatbot.html")

# -----------------------------------
# Chatbot API
# -----------------------------------
@bp.route("/api", methods=["POST"])
def chat_api():
    data = request.get_json(silent=True)
    if not data or "message" not in data:
        return jsonify({"reply": "Please type a message."})

    msg = data["message"].lower().strip()

    # Reset
    if msg == "reset":
        session.clear()
        return jsonify({"reply": "🔄 All details cleared. Ask again!"})

    # Greeting
    if msg in ["hi", "hello", "hey"]:
        return jsonify({
            "reply": (
                "Hello! 👋\n\n"
                "Ask me about:\n"
                "• Women schemes\n"
                "• Student schemes\n"
                "• Farmer schemes\n"
                "• Health schemes\n\n"
                "Or type: check eligibility"
            )
        })

    # Detect scheme category
    for key in SCHEMES:
        if key in msg:
            session["intent"] = key
            schemes = "\n".join([f"• {s}" for s in SCHEMES[key]])
            return jsonify({
                "reply": f"📌 {key.capitalize()} Schemes\n\n{schemes}\n\nType: check eligibility"
            })

    # Eligibility
    if msg == "check eligibility":
        if "age" not in session:
            return jsonify({"reply": "Please tell me your age."})
        if "occupation" not in session:
            return jsonify({"reply": "Please tell me your occupation."})
        return show_eligibility()

    # Age
    if msg.isdigit():
        session["age"] = int(msg)
        return jsonify({"reply": "Got it! Now tell me your occupation."})

    # Occupation
    if "age" in session and "occupation" not in session:
        session["occupation"] = msg
        return show_eligibility()

    return jsonify({"reply": "❓ I didn’t understand. Try typing 'women schemes' or 'reset'."})


def show_eligibility():
    intent = session.get("intent", "general")
    age = session.get("age")
    occupation = session.get("occupation")

    schemes = SCHEMES.get(intent, [])
    schemes_text = "\n".join([f"• {s}" for s in schemes])

    return jsonify({
        "reply": (
            "🧾 Profile Summary\n"
            f"• Age: {age}\n"
            f"• Occupation: {occupation}\n\n"
            "🎯 Eligible Schemes\n"
            f"{schemes_text}\n\n"
            "Type: reset to start over"
        )
    })
