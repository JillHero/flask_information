from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pymysql import  install_as_MySQLdb
from redis import StrictRedis
install_as_MySQLdb()

app = Flask(__name__)
db = SQLAlchemy(app)



class Config():
    debug = True
    SQLALCHEMY_DATABASE_URI = "mysql://root:3471515q@127.0.0.1:3306/information_rewiew"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379



app.config.from_object(Config)
redis_store = StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)


@app.route("/")
def index():
    return "index page"


if __name__ == '__main__':
    app.run()