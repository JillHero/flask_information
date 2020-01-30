from flask import render_template, request, current_app, session, redirect, url_for, g

from info.modules.admin import admin_blu
from info.models import User
from info.utils.common import user_login_data



@admin_blu.route("/index")
@user_login_data
def index():
    user = g.user


    return render_template("admin/index.html",user=user.to_dict())

@admin_blu.route("/login",methods=["GET","POST"])

def login():
    if request.method == "GET":
        user_id = session.get("user_id", None)
        is_admin = session.get("is_admin", False)
        if user_id and is_admin:
            return redirect(url_for("admin.index"))
        return render_template("admin/login.html")

    username =  request.form.get("username")
    password = request.form.get("password")

    if not all([username,password]):
        return render_template("admin/login.html",errmsg="参数错误")
    try:
        user = User.query.filter(User.mobile == username,User.is_admin == True).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/login.html",errmsg="用户查询失败")

    if not user:
        return render_template("admin/login.html",errmsg="为查询到用户信息")
    if not user.check_passowrd(password):
        return render_template("admin/login.html",errmsg="用户密码错误")

    session["user_id"] =  user.id
    session["mobile"] = user.mobile
    session["nick_name"] = user.nick_name
    session["is_admin"] = user.is_admin

    return redirect(url_for("admin.index"))


    
    

