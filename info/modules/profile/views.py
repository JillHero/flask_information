from flask import render_template, g, redirect, request, jsonify, current_app

from . import profile_blu
from ... import db, constants
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
    
    
   