from flask import session

from . import index_blu


@index_blu.route("/")
def index():
    session["name"] = "jill"
    return "index page"
