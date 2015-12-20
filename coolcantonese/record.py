#! /usr/bin/env python
# -*- coding:utf-8 -*-
import requests
import json


class JsonSerializable(object):

    def json(self):
        return json.dumps(
            self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class Record(JsonSerializable):

    """coolcantonese chat record"""

    TRANSLATION_REQUEST = 0
    TRANSLATION_RESULT = 1
    CHAT_REQUEST = 2
    CHAT_RESPONSE = 3

    def __init__(self, uid, content, rtype=TRANSLATION_REQUEST, reply=None):
        super(Record, self).__init__()
        self.uid = uid
        self.content = content
        self.type = rtype
        self.reply = reply


class RecordService(object):

    """coolcantonese record restful services client"""

    def __init__(self, services_url_prefix):
        super(RecordService, self).__init__()
        self.services_url_prefix = services_url_prefix

    def add_record(self, record):
        url = "%s/records" % self.services_url_prefix
        headers = {'Content-type': 'application/json'}
        data = record.json()
        # print data
        r = requests.post(url, data=data, headers=headers)
        # print r.status_code
        # print r.headers
        # print r.text
        # print r.json()
        return r.status_code != 200 or r.status_code != 201


def main():
    host = "http://localhost:8080/coolcantonese/services"
    services = RecordService(host)
    reply = None
    reply = Record("translator", "我钟意你", Record.TRANSLATION_RESULT)
    record = Record("kk17", "我喜欢你", Record.TRANSLATION_REQUEST, reply)
    services.add_record(record)

if __name__ == '__main__':
    main()
