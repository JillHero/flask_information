import time
from datetime import datetime, timedelta

from flask import render_template, request, current_app, session, redirect, url_for, g, jsonify, abort

from info import constants, db
from info.modules.admin import admin_blu
from info.models import User, News, Category
from info.utils.common import user_login_data
from info.utils.image_storage import storage
from info.utils.response_code import RET


@admin_blu.route("/index")
@user_login_data
def index():
    user = g.user

    return render_template("admin/index.html", user=user.to_dict())


@admin_blu.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('admin/login.html')

    # 取到登录的参数
    username = request.form.get("username")
    password = request.form.get("password")
    if not all([username, password]):
        return render_template('admin/login.html', errmsg="参数不足")

    try:
        user = User.query.filter(User.mobile == username).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/login.html', errmsg="数据查询失败")

    if not user:
        return render_template('admin/login.html', errmsg="用户不存在")

    if  user.check_passowrd(password):
        return render_template('admin/login.html', errmsg="密码错误")

    if not user.is_admin:
        return render_template('admin/login.html', errmsg="用户权限错误")

    session["user_id"] = user.id
    session["nick_name"] = user.nick_name
    session["mobile"] = user.mobile
    session["is_admin"] = True

    return redirect(url_for("admin.index"))

@admin_blu.route("/user_count")
def user_count():
    total_count = 0
    mon_count = 0
    day_count = 0
    t = time.localtime()
    begin_mon_date = datetime.strptime(("%d-%02d-1" % (t.tm_year, t.tm_mon)), "%Y-%m-%d")
    try:
        total_count = User.query.filter(User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)

    try:
        mon_count = User.query.filter(User.is_admin == False, User.create_time > begin_mon_date).count()
    except Exception as e:
        current_app.logger.error(e)

    begin_day_date = datetime.strptime(("%d-%02d-%02d" % (t.tm_year, t.tm_mon, t.tm_mday)), "%Y-%m-%d")
    try:
        day_count = User.query.filter(User.is_admin == False, User.create_time > begin_day_date).count()
    except Exception as e:
        current_app.logger.error(e)

    active_time = []
    active_count = []
    datetime.now()
    begin_today_date = datetime.strptime("%d-%02d-%02d" % (t.tm_year, t.tm_mon, t.tm_mday), "%Y-%m-%d")
    for i in range(0, 31):
        begin_date = begin_today_date - timedelta(days=i)
        end_date = begin_today_date - timedelta(days=i - 1)
        count = User.query.filter(User.is_admin == False, User.last_login >= begin_date,
                                  User.last_login < end_date).count()
        active_count.append(count)
        active_time.append(begin_date.strftime("%Y-%m-%d"))

    active_count.reverse()
    active_time.reverse()

    data = {
        "total_count": total_count,
        "mon_count": mon_count,
        "day_count": day_count,
        "active_time": active_time,
        "active_count": active_count

    }
    return render_template("admin/user_count.html", data=data)


@admin_blu.route("/user_list")
def user_lists():
    keywords = request.args.get("keywords", None)
    page = request.args.get("page", 1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    users = []
    current_page = 1
    total_page = 1

    filters = [News.status != 0]
    if keywords:
        filters.append(News.query.contains(keywords))
    try:
        paginate = User.query.filter(*filters).order_by(User.create_time.desc()).paginate(page,
                                                                                          constants.ADMIN_NEWS_PAGE_MAX_COUNT,
                                                                                          False)
        users = paginate.items
        current_page = paginate.page
        total_page = paginate.pages

    except Exception as e:
        current_app.logger.error(e)

    user_dict_li = []
    for user in users:
        user_dict_li.append(user.to_admin_dict())

    data = {
        "users": user_dict_li,
        "total_page": total_page,
        "current_page": current_page
    }

    return render_template("admin/user_list.html", data=data)


@admin_blu.route("/news_review")
def review_list():
    page = request.args.get("p", 1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    news_list = []
    current_page = 1
    total_page = 1
    try:
        paginage = News.query.filter(News.status != 0).order_by(News.create_time.desc()).paginate(page,
                                                                                                  constants.ADMIN_NEWS_PAGE_MAX_COUNT,
                                                                                                  False)
        news_list = paginage.items
        current_page = paginage.page
        total_page = paginage.pages

    except Exception as e:
        current_app.logger.error(e)

    news_dict_li = []

    for news in news_list:
        news_dict_li.append(news.to_review_dict())

    data = {
        "total_page": total_page,
        "current_page": current_page,
        "news_list": news_dict_li

    }
    return render_template("admin/news_review.html", data=data)


@admin_blu.route("/news_review_detail/<int:news_id>")
def news_review_detail(news_id):
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
    if not news:
        return render_template("admin/news_review_detail.html", data={"errmsg": "未查询到此新闻"})
    data = {
        "news": news.to_dict()
    }

    return render_template("admin/news_review_detail.html", data=data)


@admin_blu.route("/news_review_action", methods=["POST"])
def news_review_action():
    news_id = request.json.get("news_id")
    action = request.json.get("action")

    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if action not in ("accept", "reject"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="未查询到数据")

    if action == "accept":
        news.status = 0
        db.session.commit()

    else:
        reason = request.json.get("reason")
        if not reason:
            return jsonify(errno=RET.PARAMERR, errmsg="请输入拒绝原因")
        news.status = -1
        news.reason = reason
        db.session.commit()
    return jsonify(errno=RET.OK, errmsg="成功")


@admin_blu.route("/news_edit")
def news_edit():
    keywords = request.args.get("keywords", None)
    page = request.args.get("page", 1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    news = []
    current_page = 1
    total_page = 1

    filters = [News.status == 0]
    if keywords:
        filters.append(News.title.contains(keywords))
    try:
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page,
                                                                                          constants.ADMIN_NEWS_PAGE_MAX_COUNT,
                                                                                          False)
        news = paginate.items
        current_page = paginate.page
        total_page = paginate.pages

    except Exception as e:
        current_app.logger.error(e)

    user_dict_li = []
    for new in news:
        user_dict_li.append(new.to_basic_dict())

    context = {
        "news_list": user_dict_li,
        "total_page": total_page,
        "current_page": current_page
    }

    return render_template("admin/news_edit.html", data=context)


@admin_blu.route("/news_edit_detail", methods=["GET", "POST"])
def news_edit_detail():
    if request.method == "GET":
        news_id = request.args.get("news_id")
        if not news_id:
            abort(404)
        try:
            news_id = int(news_id)
        except Exception as e:
            return render_template("admin/news_edit_detail.html", errmsg="参数错误")
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return render_template("admin/news_edit_detail.html", errmsg="查询数据错误")

        if not news:
            return render_template("admin/news_edit_detail.html", errmsg="未查询到数据")
        categories = []
        try:
            categoris = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return render_template("admin/news_edit_detail.html", errmsg="查询数据错误")
        for category in categoris:
            cate_dict = category.to_dict()
            if category.id == news.category_id:
                cate_dict["is_selected"] = True

            categories.append(cate_dict)

        categories.pop(0)

        data = {
            "news": news.to_dict(),
            "categories": categories
        }
        return render_template("admin/news_edit_detail.html", data=data)

    title = request.form.get("title")
    news_id = request.form.get("news_id")
    digest = request.form.get("digest")
    content = request.form.get("content")
    index_image = request.files.get("index_image")
    category_id = request.form.get("category_id")

    if not all([title, news_id, digest, content, category_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    news = None

    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="未查询到数据")

    if index_image:
        
        try:
            index_image = index_image.read()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

        try:
            key = storage(index_image)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="上传图片错误")
        news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
    news.title = title
    news.digest = digest
    news.content = content
    news.category_id = category_id
    
    try:
        db.session.commit()
    
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
    
    return jsonify(errno=RET.OK, errmsg="成功")
    
        
@admin_blu.route("/news_type",methods=["GET","POST"])
def news_type():
    if request.method == "GET":
        try:
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return render_template("admin/news_type.html",errmsg="查询数据错误")
    
        category_dict_li = []
        for category in categories:
            category_dict_li.append(category)
    
        category_dict_li.pop(0)
    
        data = {
            "categories":category_dict_li
    
        }
        return render_template("admin/news_type.html",data=data)
    
    cname = request.json.get("name")
    cid = request.json.get("id")
    
    if not cname:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    category = None
    if cid:
        try:
            cid = int(cid)
            category = Category.query.get(cid)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
        
        if not category:
            return jsonify(errno=RET.NODATA, errmsg="未查询到分类数据")
        
        category.name = cname
    else:
        category = Category()
        category.name = cname
        db.session.add(category)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        
    return jsonify(errno=RET.OK, errmsg="成功")


