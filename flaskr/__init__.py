import os
from flask import Flask
from flask_mail import Mail
from flask_mysqldb import MySQL

mail = Mail()
mysql = MySQL()


def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev"),

        MYSQL_HOST=os.getenv("MYSQL_HOST", "localhost"),
        MYSQL_USER=os.getenv("MYSQL_USER", "root"),
        MYSQL_PASSWORD=os.getenv("MYSQL_PASSWORD", "shushant@2006"),
        MYSQL_DB=os.getenv("MYSQL_DB", "sarkari_sahayata"),

        MAIL_SERVER="smtp.gmail.com",
        MAIL_PORT=587,
        MAIL_USE_TLS=True,
        MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
        MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
        MAIL_DEFAULT_SENDER=os.getenv("MAIL_USERNAME"),
    )

    if test_config:
        app.config.update(test_config)

    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    mail.init_app(app)
    mysql.init_app(app)

    from . import db
    db.init_app(app)

    # Register Blueprints
    from .auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from .home import bp as home_bp
    app.register_blueprint(home_bp)

    from .categories import bp as categories_bp
    app.register_blueprint(categories_bp)

    from .chatbot import bp as chatbot_bp
    app.register_blueprint(chatbot_bp)

    from .admin import admin_bp
    app.register_blueprint(admin_bp)

    return app