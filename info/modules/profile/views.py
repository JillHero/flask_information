from flask import render_template, g, redirect, request

from . import  profile_blu
from ...utils.common import user_login_data


@profile_blu.route("/info")
@user_login_data
def user_info():

    user = g.user
    if not user:
        return redirect("/")


    data = {"user_info":user.to_dict()}

    return render_template("news/user.html",data=data)


@profile_blu.route("/user_info",methods=["POST"])
@user_login_data
def base_info():
    if request.method == "GET":

        return render_template("news/user_base_info.html",data={"user_info":g.user.to_dict()})


