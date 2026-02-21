import os
from flask import Flask
from flask_mail import Mail
from flask_mysqldb import MySQL

mail = Mail()
mysql = MySQL()


def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev'
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    mail.init_app(app)
    mysql.init_app(app)

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

    return app