from flask import request, abort, current_app, make_response

from . import passport_blu
from info.utils.captcha.captcha import captcha
from info import redis_store, constants


@passport_blu.route('/image_code')
def get_image_code():
    image_code_id = request.args.get(("imageCodeId"), None)
    if not image_code_id:
        abort(403)

    name, text, image = captcha.generate_captcha()

    try:
        redis_store.set("ImageCode_" + image_code_id,text, constants.IMAGE_CODE_REDIS_EXPIRES)

    except Exception as e:
        current_app.logger.debug(e)
        abort(500)


    response = make_response(image)
    response.headers["Content-Type"] = "image/jpg"

    return response
