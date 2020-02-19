import logging

from redis import StrictRedis


class Config():
    SECRET_KEY = "DR0NLoBAgMxv2w1LYunZvnhBRiatRRWLWEjZjAMCnO1GMUYQBSc23Nd+ujqqqlCEUiH3bmhGouHTkApjZaaaVg=="
    SQLALCHEMY_DATABASE_URI = "mysql://root:3471515q@127.0.0.1:3306/information"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TRARDOWN = True
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    SESSION_TYPE = "redis"
    SESSION_USE_SINGER = True
    SESSION_PERMANENT = False
    PRRMANENT_SESSION_LIFETIONE = 86400 * 2
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    LOG_LEVEL = logging.DEBUG


class DevelopmentConfig(Config):

    DEBUG = False


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "mysql://root:3471515q@127.0.0.1:3306/information_rewiew"
    LOG_LEVEL = logging.INFO




config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig
}
