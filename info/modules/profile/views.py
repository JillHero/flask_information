from flask import render_template, g, redirect, request, jsonify

from . import  profile_blu
from ... import db
from ...utils.common import user_login_data
from ...utils.response_code import RET


@profile_blu.route("/info")
@user_login_data
def get_user_info():

    user = g.user
    if not user:
        return redirect("/")


    data = {"user_info":user.to_dict()}

    return render_template("news/user.html",data=data)


@profile_blu.route("/base_info",methods=["GET","POST"])
@user_login_data
def base_info():
    if request.method == "GET":

        return render_template("news/user_base_info.html",data={"user_info":g.user.to_dict()})


    elif request.method == "POST":

        nick_name = request.json.get("nick_name")
        signature = request.json.get("signature")
        gender = request.json.get("gender")

        if not all([nick_name,signature,gender]):
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")


        if gender not in ["WOMAN","MAN"]:
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

        user = g.user

        user.signature = signature
        user.nick_name = nick_name
        user.gender = gender

        db.session.commit()

        return jsonify(errno=RET.OK, errmsg="成功")





