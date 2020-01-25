import random
import re
from datetime import datetime

from flask import request, abort, current_app, make_response, jsonify, session

from . import passport_blu
from info.utils.captcha.captcha import captcha
from info import redis_store, constants, db
from info.utils.response_code import RET
from info.models import User
from ...utils.yuntongxun import sms
from ...utils.yuntongxun.sms import CCP


@passport_blu.route('/image_code')
def get_image_code():
    image_code_id = request.args.get(("imageCodeId"), None)
    if not image_code_id:
        abort(403)

    name, text, image = captcha.generate_captcha()
    current_app.logger.debug("图片验证码内容：%s" % text)

    try:
        redis_store.set("ImageCode_" + image_code_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)

    except Exception as e:
        current_app.logger.debug(e)
        abort(500)

    response = make_response(image)
    response.headers["Content-Type"] = "image/jpg"

    return response


@passport_blu.route("/smscode", methods=["POST"])
def send_sms_code():
    params_dict = request.json
    mobile = params_dict.get("mobile")
    image_code = params_dict.get("image_code")
    image_code_id = params_dict.get("image_code_id")

    if not all([mobile, image_code_id, image_code]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")
    if not re.match("1[35678]\\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号校验失败")

    try:
        real_image_code = redis_store.get("ImageCode_" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")

    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg="验证码已过期")

    if real_image_code.upper() != image_code.upper():
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    redis_store.delete("ImageCode_" + image_code_id)

    sms_code_str = "%06d" % random.randint(0, 999999)
    current_app.logger.debug("短信验证码是%s" % sms_code_str)
    try:
        redis_store.set("SMS_" + mobile, sms_code_str, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="数据保存失败")

    # result = CCP().send_template_sms(mobile, [sms_code_str, constants.SMS_CODE_REDIS_EXPIRES],1)
    # print(result)
    #
    # if result != 0:
    #     return jsonify(errno=RET.THIRDERR, errmsg="发送短信失败")

    return jsonify(errno=RET.OK, errmsg="发送短信成功")


@passport_blu.route("/register", methods=["POST"])
def register():
    param_dict = request.json
    mobile = param_dict.get("mobile")
    sms_code = param_dict.get("smscode")
    password = param_dict.get("password")

    if not all([mobile, sms_code, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if not re.match("1[13579]\\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式不正确")

    try:
        real_sms_code = redis_store.get("SMS_" + mobile)
    except Exception as e:
        current_app.logger.error(e)

        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")
    if not real_sms_code:
        return jsonify(errno=RET.NODATA, errmsg="验证码已过期")

    if real_sms_code != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    user = User()
    user.mobile = mobile
    user.nick_name = mobile
    user.last_login = datetime.now()
    user.password = password

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")

    session["user_id"] = user.id
    session["mobile"] = user.mobile
    session["nick_name"] = user.nick_name

    return jsonify(errno=RET.OK, errmsg="注册成功")


@passport_blu.route("/login", methods=["POST"])
def login():
    param_dict = request.json
    mobile = param_dict.get("mobile")
    passport = param_dict.get("password")

    if not all([mobile, passport]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if not re.match("1[13579]\\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式不正确")

    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")
    if not user:
        return jsonify(errno=RET.NODATA, errmsg="用户不存在")

    if not user.check_passowrd(passport):
        return jsonify(errno=RET.PWDERR, errmsg="密码错误")

    session["user_id"] = user.id
    session["mobile"] = user.mobile
    session["nick_name"] = user.nick_name
    user.last_login = datetime.now()
    # try:
    #     db.session.commit()
    # except Exception as e:
    #     db.session.rollback()
    #     current_app.logger.error(e)

    return jsonify(errno=RET.OK, errmsg="登陆成功")


@passport_blu.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("mobile", None)
    session.pop("nick_name", None)

    return jsonify(errno=RET.OK, errmsg="成功")
