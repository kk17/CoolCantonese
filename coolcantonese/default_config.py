# -*- coding: utf-8 -*-

default_config = {
    "enable_client": False,
    "use_redis_session": False,
    "redis_host": "localhost",
    "redis_port": 6379,
    "redis_db": 1,
    "redis_password": "",
    "enable_record_services": False,
    "enable_tuling_robot": False,
    "tuling_api_key": "",
    "use_baidu_translator": False,
    "baidu_app_id": "",
    "baidu_app_secret": "",
    "host": "0.0.0.0",
    "port": "8888",
    "phonetic_data_path": "coolcantonese/data/phonetic-data.txt",
    "translation_expire_seconds": 60*5,
    "audio_folder": "/tmp",
    "file_session_path": "/tmp/coolcantonese_session",
    "wechat_token": "kk17",
    "subscribe_msg": u"谢谢关注粤讲粤酷，发送？获取帮助",
    "audio_url_prefix": "http://localhost:8888",
    "debug": False
}
