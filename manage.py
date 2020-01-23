from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pymysql import  install_as_MySQLdb
install_as_MySQLdb()

app = Flask(__name__)
db = SQLAlchemy(app)



class Config():
    debug = True
    SQLALCHEMY_DATABASE_URI = "mysql://root:3471515q@127.0.0.1:3306/information_rewiew"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


app.config.from_object(Config)



@app.route("/")
def index():
    return "index page"


if __name__ == '__main__':
    app.run()