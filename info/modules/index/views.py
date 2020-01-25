from flask import session, render_template, current_app

from . import index_blu
from ...models import User


@index_blu.route("/")
def index():
    user_id = session.get("user_id")
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    data = {
        "user_info":user.to_dict() if user else None

    }




    return render_template("index.html",data=data)


@index_blu.route("/favicon.ico")
def favicon():
    return current_app.send_static_file("news/favicon.ico")


