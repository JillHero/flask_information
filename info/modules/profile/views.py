from flask import render_template, g, redirect, request, jsonify, current_app

from . import profile_blu
from ... import db, constants
from ...models import Category, News
from ...utils.common import user_login_data
from ...utils.image_storage import storage
from ...utils.response_code import RET


@profile_blu.route("/info")
@user_login_data
def get_user_info():
    user = g.user
    if not user:
        return redirect("/")

    data = {"user_info": user.to_dict()}

    return render_template("news/user.html", data=data)


@profile_blu.route("/base_info", methods=["GET", "POST"])
@user_login_data
def base_info():
    if request.method == "GET":

        return render_template("news/user_base_info.html", data={"user_info": g.user.to_dict()})


    elif request.method == "POST":

        nick_name = request.json.get("nick_name")
        signature = request.json.get("signature")
        gender = request.json.get("gender")

        if not all([nick_name, signature, gender]):
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

        if gender not in ["WOMAN", "MAN"]:
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

        user = g.user

        user.signature = signature
        user.nick_name = nick_name
        user.gender = gender

        db.session.commit()

        return jsonify(errno=RET.OK, errmsg="成功")


@profile_blu.route("/pic_info", methods=["GET", "POST"])
@user_login_data
def pic_info():
    if request.method == "GET":
        return render_template("news/user_pic_info.html", data={"user_info": g.user.to_dict()})

    try:
        file = request.files.get("avatar")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    try:
        key = storage(file)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传头像失败")

    g.user.avatar_url = key
    db.session.commit()
    return jsonify(errno=RET.OK, errmsg="成功", data={"avatar_url": constants.QINIU_DOMIN_PREFIX + key})


@profile_blu.route("/pass_info", methods=["GET", "POST"])
@user_login_data
def modify_password():
    if request.method == "GET":
        return render_template("news/user_pass_info.html")

    news_password = request.json.get("new_password")
    old_password = request.json.get("old_password")

    if not all([news_password, old_password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    user = g.user
    if not user.check_passowrd(old_password):
        return jsonify(errno=RET.PWDERR, errmsg="原密码错误")

    user.password = news_password
    db.session.commit()
    return jsonify(errno=RET.OK, errmsg="成功")


@profile_blu.route("/collection")
@user_login_data
def user_collection():
    page = request.args.get("p", 1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    user = g.user
    news_list = []
    total_page = 1
    current_page = 1
    try:
        paginage = user.collection_news.paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)

        current_page = paginage.page
        total_page = paginage.pages
        news_list = paginage.items
    except Exception as e:
        current_app.logger.error(e)
    news_dict_li = []
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())

    data = {
        "total_page": total_page,
        "current_page": current_page,
        "collections": news_dict_li
    }

    return render_template("news/user_collection.html", data=data)


@profile_blu.route("/news_release",methods=["GET","POST"])
@user_login_data
def news_release():
    if request.method == "GET":
        categories = []
        try:

            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)

        category_dict_li = []

        for category in categories:
            category_dict_li.append(category.to_dict())
        category_dict_li.pop(0)
        return render_template("news/user_news_release.html",data={"categories":category_dict_li})

    title = request.form.get("title")
    category_id = request.form.get("category_id")
    digest = request.form.get("digest")
    content = request.form.get("content")
    index_image = request.files.get("index_image")
    source = "个人发布"

    if not all([title,category_id,digest,content,index_image,source]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")
    try:
        category_id = int(category_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")
    
    try:
        index_image_data = index_image.read()
        key = storage(index_image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="第三方错误")

    news = News()
    news.title = title
    news.digest = title
    news.source = source
    news.category_id = category_id
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
    news.user_id = g.user.id
    news.content = content
    
    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据库保存失败")
    
    return jsonify(errno=RET.OK, errmsg="成功")
    