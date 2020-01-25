from flask import session, render_template, current_app,jsonify

from . import index_blu
from ...models import User, News
from ...utils.response_code import RET


@index_blu.route("/")
def index():
    user_id = session.get("user_id")
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
    news_list = []
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(6)
    except Exception as e:
        current_app.logger.error(e)

    news_dict_li = []
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())
    data = {
        "user_info":user.to_dict() if user else None,
        "news_dict_li":news_dict_li

    }
    return render_template("index.html",data=data)






@index_blu.route("/favicon.ico")
def favicon():
    return current_app.send_static_file("news/favicon.ico")


