from flask import session
from pymysql import install_as_MySQLdb
from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate
from info import app, db

install_as_MySQLdb()

manage = Manager(app)
Migrate(app, db)
manage.add_command("db", MigrateCommand)


@app.route("/")
def index():
    session["name"] = "jill"
    return "index page"


if __name__ == '__main__':
    manage.run()
