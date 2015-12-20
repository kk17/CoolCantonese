# -*- coding: utf-8 -*-

import os.path as path
import pytest
from coolcantonese.config import AttrDict
from coolcantonese.session import SmartSession


@pytest.fixture
def file_session(tmpdir):
    filepath = path.join(tmpdir.strpath, "coolcantonese_session")
    config = {
        "use_redis_session": False,
        "redis_host": "localhost",
        "redis_port": 6379,
        "redis_db": 1,
        "redis_password": "",
        "phonetic_data_path": "coolcantonese/data/phonetic-data.txt",
        "file_session_path": filepath,
    }
    cfg = AttrDict(config)
    return SmartSession(cfg)


def test_file_session(file_session):
    key = "kk"
    value = 17
    print(file_session.get(key))
    assert not file_session.exists(key)
    file_session.set(key, value)
    assert file_session.get(key) == value
    assert file_session[key] == value
    assert file_session.exists(key)
    file_session.delete(key)
    assert not file_session.exists(key)
    file_session.expire(key, 10)


# @pytest.fixture
# def redis_session(tmpdir):
#     filepath = path.join(tmpdir.strpath, "coolcantonese_session")
#     config = {
#         "use_redis_session": True,
#         "redis_host": "localhost",
#         "redis_port": 6379,
#         "redis_db": 1,
#         "redis_password": "",
#         "phonetic_data_path": "coolcantonese/data/phonetic-data.txt",
#         "file_session_path": filepath,
#     }
#     cfg = AttrDict(config)
#     return SmartSession(cfg)


# def test_redis_session(redis_session):
#     key = "kk"
#     value = 17
#     print(redis_session.get(key))
#     assert not redis_session.exists(key)
#     redis_session.set(key, value)
#     assert redis_session.get(key) == value
#     assert redis_session[key] == value
#     assert redis_session.exists(key)
#     redis_session.delete(key)
#     assert not redis_session.exists(key)
#     redis_session.set(key, value)
#     redis_session.expire(key, 1)
#     import time
#     time.sleep(1)
#     assert not redis_session.exists(key)
