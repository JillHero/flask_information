from flask import session

from . import index_blu
from ... import redis_store


@index_blu.route("/")
def index():
    session["name"] = "jill"
    return "index page"
