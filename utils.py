import hmac
import time
import base64
from urllib.parse import quote


def get_token(id, access_key):  # 官方文档给出的核心秘钥计算算法
    version = "2018-10-31"
    res = "products/%s" % id  # 通过产品ID访问产品API
    # 用户自定义token过期时间
    et = str(int(time.time()) + 3600)
    # 签名方法，支持md5、sha1、sha256
    method = "sha1"
    # 对access_key进行decode
    key = base64.b64decode(access_key)

    # 计算sign
    org = et + "\n" + method + "\n" + res + "\n" + version
    sign_b = hmac.new(key=key, msg=org.encode(), digestmod=method)
    sign = base64.b64encode(sign_b.digest()).decode()

    # value 部分进行url编码，method/res/version值较为简单无需编码
    sign = quote(sign, safe="")
    res = quote(res, safe="")

    # token参数拼接
    token = "version=%s&res=%s&et=%s&method=%s&sign=%s" % (
        version,
        res,
        et,
        method,
        sign,
    )
    return token


def get_timestamp():
    # "time": 1706673129818
    return int(time.time() * 1000)
    # return int(time.time())
