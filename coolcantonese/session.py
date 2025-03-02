# -*- coding: utf-8 -*-

try:
    import anydbm as dbm
    assert dbm
except ImportError:
    import dbm
import pickle
import logging
from redis import StrictRedis
from werobot.session import SessionStorage
from coolcantonese.util import to_string_type
import diskcache


logger = logging.getLogger(__name__)


class Session(SessionStorage):
    """extend for werobot SessionStorage"""
    def __init__(self):
        super(Session, self).__init__()

    def expire(self, key, expire_seconds):
        raise NotImplementedError()

    def exists(self, key):
        raise NotImplementedError()


class RedisSession(StrictRedis, Session):

    def get(self, name):
        pickled_value = super(RedisSession, self).get(name)
        if pickled_value is None:
            return None
        return pickle.loads(pickled_value)

    def set(self, name, value, ex=None, px=None, nx=False, xx=False):
        return super(RedisSession, self).set(
            name, pickle.dumps(value), ex, px, nx, xx
        )


class FileSession(Session):

    """
    FileSession 会把你的 Session 数据以 dbm 形式储存在文件中。

    :param filepath: 文件名， 默认为 ``coolcantonese_session``
    """
    def __init__(self, filepath='coolcantonese_session'):
        self.db = dbm.open(filepath, "c")

    def get(self, key):
        key = to_string_type(key)
        try:
            session_json = self.db[key]
        except KeyError:
            return None
        return pickle.loads(session_json)

    def set(self, key, value):
        key = to_string_type(key)
        self.db[key] = pickle.dumps(value)

    def delete(self, key):
        key = to_string_type(key)
        del self.db[key]

    def expire(self, key, expire_seconds):
        pass

    def exists(self, key):
        key = to_string_type(key)
        # logger.debug("db.keys:%s", self.db.keys())
        return key in self.db


class DiskcacheSession(Session):
    """Session implementation using diskcache."""

    def __init__(self, cache_dir=None):
        # Use a temporary directory if no cache_dir is specified
        self.cache = diskcache.Cache(cache_dir)

    def get(self, key):
        try:
            return self.cache.get(key)
        except KeyError:
            return None

    def set(self, key, value, expire=None):
        self.cache.set(key, value, expire=expire)

    def delete(self, key):
        try:
            del self.cache[key]
        except KeyError:
            pass  # Key doesn't exist, nothing to delete

    def expire(self, key, expire_seconds):
        self.cache.expire(key, expire_seconds)

    def exists(self, key):
        return key in self.cache

    def close(self):
        self.cache.close()


class SmartSession(Session):
    """docstring for Session"""
    def __init__(self, cfg):
        super(SmartSession, self).__init__()
        if cfg.session_impl.lower() == 'redis':
            self._session = RedisSession(
                cfg.redis_host, cfg.redis_port,
                cfg.redis_db, cfg.redis_password)
        elif cfg.session_impl.lower() == 'file':
            self._session = FileSession(cfg.file_session_path)
        else:
            # default to use DiskcacheSession
            self._session = DiskcacheSession()

    def get(self, key):
        return self._session.get(key)

    def set(self, key, value, expire=None):
        return self._session.set(key, value, expire=expire)

    def delete(self, key):
        return self._session.delete(key)

    def expire(self, key, expire_seconds):
        return self._session.expire(key, expire_seconds)

    def exists(self, key):
        return self._session.exists(key)