from flask import session
from pymysql import install_as_MySQLdb
from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate
from info import create_app, db

install_as_MySQLdb()

app = create_app("development")
manage = Manager(app)
Migrate(app, db)
manage.add_command("db", MigrateCommand)




if __name__ == '__main__':
    manage.run()
