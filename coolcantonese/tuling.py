#! /usr/bin/env python
# -*- coding:utf-8 -*-
import requests


class TulingService(object):

    """Tuling robot service client"""

    def __init__(self, api_key):
        super(TulingService, self).__init__()
        self.api_key = api_key

# """
# key	必须	32	1ca80891c02eb2edb736b8ce41591426	开发者先注册帐号，激活之后即可获得
# info	必须	1~30	打招呼“你好”，查天气“北京今天天气”	请求内容，编码方式为UTF-8
# userid	上下文必须	1~32	eb2edb736	此userid针对开发者自己的每一个用户
# loc	非必须	1~30	北京中关村	位置信息，编码方式为UTF-8
# lon	非必须	-	东经116.234632（小数点后保留6位），需要写为116234632	经度信息
# lat	非必须	-	北纬40.234632（小数点后保留6位），需要写为40234632	纬度信息

# 100000	文本类数据
# 305000	列车
# 306000	航班
# 200000	网址类数据
# 302000	新闻
# 308000	菜谱、视频、小说
# 40001	key的长度错误（32位）
# 40002	请求内容为空
# 40003	key错误或帐号未激活
# 40004	当天请求次数已用完
# 40005	暂不支持该功能
# 40006	服务器升级中
# 40007	服务器数据格式异常
# """

    def send_msg(self, uid, msg):
        url = "http://www.tuling123.com/openapi/api"
        headers = {'Content-type': 'application/json'}
        params = {"key": self.api_key, "info": msg, "userid": uid}
        r = requests.get(url, params=params, headers=headers)
        if r.status_code == 200:
            json_data = r.json()
            code = json_data["code"]
            if code >= 100000:
                return (True, json_data["text"])
            elif code == 40004:
                return (False, json_data["text"])
        return (False, u"抱歉暂时无法提供服务")
