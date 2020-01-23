from flask import session, render_template

from . import index_blu


@index_blu.route("/")
def index():
    return render_template("index.html")
