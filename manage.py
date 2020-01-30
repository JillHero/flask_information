from flask import session
from pymysql import install_as_MySQLdb
from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate
from info import create_app, db,models
from info.models import User

install_as_MySQLdb()

app = create_app("development")
manage = Manager(app)
Migrate(app, db)
manage.add_command("db", MigrateCommand)

@manage.option("-n","-name",dest="name")
@manage.option("-p","-password",dest="password")
def createsuperuser(name,password):
    if not all([name,password]):
        return "参数不足"
    user =User()
    user.nick_name = name
    user.mobile = name
    user.password = password
    user.is_admin = True

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)



if __name__ == '__main__':
    manage.run()
