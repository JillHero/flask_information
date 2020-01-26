from flask import render_template, current_app, session

from info import constants
from info.models import News, User
from info.modules.news import news_blu


@news_blu.route("/<int:news_id>")
def news_detail(news_id):
    user_id = session.get("user_id", None)

    user = None

    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    news_list = []

    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)

    except Exception as e:
        current_app.logger.error(e)

    news_dict_li = []
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())
    data = {

        "news_dict_li": news_dict_li,
        "user_info": user.to_dict() if user else None

    }

    return render_template("news/detail.html", data=data)
