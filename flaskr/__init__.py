import os
from flask_mail import Mail
from flask import Flask
from flask_mysqldb import MySQL
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

mail = Mail()
mysql = MySQL()

# Create limiter globally (NOT inside function)
limiter = Limiter(key_func=get_remote_address)

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev'  # Change in production
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize extensions
    mail.init_app(app)
    mysql.init_app(app)
    limiter.init_app(app)  # IMPORTANT: Initialize limiter here

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import home
    app.register_blueprint(home.bp)
    app.add_url_rule('/', endpoint='index')

    from . import categories
    app.register_blueprint(categories.bp)

    from . import chatbot
    app.register_blueprint(chatbot.bp)

    from . import admin
    app.register_blueprint(admin.admin_bp)

    # ── Jinja2 custom filter: parse JSON in templates ──
    import json as _json
    def from_json_filter(value):
        if not value:
            return None
        try:
            return _json.loads(value)
        except Exception:
            return None
    app.jinja_env.filters['from_json'] = from_json_filter

    return app