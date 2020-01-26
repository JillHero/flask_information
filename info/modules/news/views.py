from flask import render_template, current_app, session, g, abort, request, jsonify

from info import constants
from info.models import News, User
from info.modules.news import news_blu
from info.utils.common import user_login_data
from info.utils.response_code import RET



@news_blu.route("/news_collect",methods=["POST"])
@user_login_data
def collect_news():

    user = g.user

    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登陆")
    news_id = request.json.get("news_id")
    action = request.json.get("action")
    if not all([news_id,action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if action not in ["collect","cancel_collect"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    try:
        news_id = int(news_id)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        news = News.query.get(news_id)

    except Exception as e:
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="为查询到新闻数据")

    if action == "collect":

        if news not in user.collection_news:
            user.collection_news.append(news)

    else:

        if news in user.collection_news:
            user.collection_news.remove(news)

    return jsonify(errno=RET.OK, errmsg="成功")


@news_blu.route("/<int:news_id>")
@user_login_data
def news_detail(news_id):
    user = g.user


    news_list = []

    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)

    except Exception as e:
        current_app.logger.error(e)

    news_dict_li = []
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())


    news = None

    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)

    if not news:
        abort(404)


    news.clicks +=1

    is_collected = False
    if user:
        if news in user.collection_news:
            is_collected = True


    data = {

        "news_dict_li": news_dict_li,
        "user_info": user.to_dict() if user else None,
        "is_collected":is_collected,
        "news":news.to_dict()

    }

    return render_template("news/detail.html", data=data)



