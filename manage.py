from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from pymysql import install_as_MySQLdb
from redis import StrictRedis
from flask_session import Session

install_as_MySQLdb()

app = Flask(__name__)
db = SQLAlchemy(app)


class Config():
    debug = True
    SECRET_KEY = "DR0NLoBAgMxv2w1LYunZvnhBRiatRRWLWEjZjAMCnO1GMUYQBSc23Nd+ujqqqlCEUiH3bmhGouHTkApjZaaaVg=="
    SQLALCHEMY_DATABASE_URI = "mysql://root:3471515q@127.0.0.1:3306/information_rewiew"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    SESSION_TYPE = "redis"
    SESSION_USE_SINGER = True
    SESSION_PERMANENT = False
    PRRMANENT_SESSION_LIFETIONE = 86400 * 2
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)


app.config.from_object(Config)
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
CSRFProtect(app)
Session(app)


@app.route("/")
def index():
    session["name"] = "jill"
    return "index page"


if __name__ == '__main__':
    app.run()
