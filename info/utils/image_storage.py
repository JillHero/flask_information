

import qiniu

access_key = "dxZ_6X0Rcp49shU6_Fz4YPvbM_Csx3bROiK2y2Rb"
secret_key = "cFJ22VQyGlpYNfQvSegFo6ake4wyKt4ycHqdfpNf"
bucket_name = "flaskreview"
def storage(data):
    try:
        q = qiniu.Auth(access_key, secret_key)
        token = q.upload_token(bucket_name)
        ret, info = qiniu.put_data(token, None, data)
        print(ret,info)
    except Exception as e:
        raise e

    if info.status_code != 200:
        raise Exception("上传图片失败")
    return ret["key"]


if __name__ == '__main__':
    file = input("请输入文件路径")
    with open(file,"rb")as f:
        storage(f.read())

