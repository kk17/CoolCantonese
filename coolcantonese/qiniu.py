#! /usr/bin/env python
# -*- coding:utf-8 -*-

from qiniu import Auth
from qiniu import BucketManager
from qiniu import put_data, put_file, etag
from os import path
import logging


class QiniuStorage(object):

    """docstring for QiniuStorage"""

    logger = logging.getLogger("wechat")

    def __init__(self, cfg):
        super(QiniuStorage, self).__init__()
        self.cfg = cfg
        self.access_key = cfg.qiniu_access_key
        self.secret_key = cfg.qiniu_secret_key
        self.bucket_name = cfg.qiniu_bucket_name
        self.bucket_domain = cfg.qiniu_bucket_domain
        self._q = Auth(self.access_key, self.secret_key)
        self._bucket = BucketManager(self._q)

    def check_existance_and_get_url(self, file_key):
        ret, info = self._bucket.stat(self.bucket_name, file_key)
        if ret and info.status_code == 200:
            return self.get_file_url(file_key)
        return None

    def get_file_url(self, file_key):
        return "http://%s/%s" % (self.bucket_domain, file_key)

    def upload_file(self, filepath, file_key=None, mime_type=None):
        if file_key is None:
            file_key = path.basename(filepath)
        token = self._q.upload_token(self.bucket_name)
        ret, info = put_file(
            token, file_key, filepath, mime_type=mime_type, check_crc=True)
        # file_exists
        if ret and info.status_code == 614:
            return self.get_file_url(file_key)
        # upload success
        assert ret['key'] == file_key
        assert ret['hash'] == etag(filepath)
        return self.get_file_url(file_key)

    def upload_and_get_url(self, filepath, file_key=None, mime_type=None):
        if file_key is None:
            file_key = path.basename(filepath)
        url = self.check_existance_and_get_url(file_key)
        if url:
            return url
        return self.upload_file(filepath, file_key, mime_type)


def main():
    from wechat_config import WechatConfig
    cfg = WechatConfig("Dev", "configs/local_wechat.conf")
    q = QiniuStorage(cfg)

    filepath = __file__
    # filepath = "C:\Users\Public\Music\Sample Music\Kalimba.mp3"
    file_key = path.basename(filepath)
    url = q.upload_and_get_url(filepath)
    # url = q.check_existance_and_get_url(file_key)
    print(url)


if __name__ == '__main__':
    main()
