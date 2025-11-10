from flask_mysqldb import MySQL
import MySQLdb.cursors
from flaskr import mysql
import click
from flask import current_app, g

def get_db():
    """Get a per-request MySQL connection and reconnect if needed."""
    if 'db' not in g:
        g.db = connect_db()
    else:
        try:
            g.db.ping(True)  # ✅ check connection, reconnect if needed
        except MySQLdb.OperationalError:
            g.db = connect_db()
    return g.db


def connect_db():
    """Create a new MySQL connection using Flask app config."""
    cfg = current_app.config
    return MySQLdb.connect(
        host=cfg.get('MYSQL_HOST', '127.0.0.1'),
        user=cfg['MYSQL_USER'],
        passwd=cfg['MYSQL_PASSWORD'],
        db=cfg['MYSQL_DB'],
        cursorclass=MySQLdb.cursors.DictCursor,  # ✅ rows as dicts
        charset='utf8mb4',
        autocommit=True
    )


def close_db(e=None):
    """Close the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        sql_script = f.read().decode('utf8')

    cur = db.cursor()
    for statement in sql_script.split(';'):
        stmt = statement.strip()
        if stmt:
            cur.execute(stmt)
    mysql.connection.commit()
    cur.close()

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

