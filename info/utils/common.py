import functools

from flask import session, current_app, g

from info.models import User


def do_index_class(index):
    if index == 0:
        return "first"
    elif index == 1:
        return "second"
    elif index == 2:
        return "third"

    return ""



def user_login_data(func):
    @functools.wraps(func)
    def wapper(*args,**kwargs):
        user_id = session.get("user_id")
        user = None
        if user_id:
            try:
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)

        g.user = user
        return func(*args,**kwargs)

    return wapper