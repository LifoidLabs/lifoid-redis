# -*- coding: utf8 -*-
"""
Redis implementation of storage backend
Author:   Romary Dupuis <romary@me.com>
Copyright (C) 2017 Romary Dupuis
"""
import os
import json
import redis
from awesomedecorators import memoized
from lifoid.data.backend import Backend
from lifoid.config import settings


class RedisBackend(Backend):
    """
    Backend based on Redis
    """
    @memoized
    def redis_server(self):
        return redis.StrictRedis(host=settings.redis.host,
                                 port=settings.redis.port,
                                 db=settings.redis.db)

    def exists(self, key):
        return self.redis_server.exists(self.prefixed(key))

    def keys(self, pattern):
        return self.redis_server.keys(pattern)

    def get(self, key, sort_key):
        value = self.redis_server.get(
            self.prefixed('{}:{}'.format(key, sort_key))
        )
        if value is not None:
            return value.decode('utf-8')
        return value

    def set(self, key, sort_key, value):
        if sort_key is not None:
            self.redis_server.zadd(self.prefixed(key), { sort_key: 0.0 })
        prev_value = self.get(key, sort_key)
        prev_obj = None
        if prev_value is not None:
            prev_obj = json.loads(prev_value)
        for sec_index in self._secondary_indexes:
            if (prev_obj is not None and
               sec_index in prev_obj.keys()):
                self.redis_server.srem(
                    self.prefixed('secondary_indexes:{}:{}'.format(
                        sec_index, prev_obj[sec_index]
                    )),
                    self.prefixed('{}:{}'.format(key, sort_key))
                )
            obj = json.loads(value)
            if sec_index in obj.keys():
                self.redis_server.sadd(
                    self.prefixed('secondary_indexes:{}:{}'.format(
                        sec_index, obj[sec_index]
                    )),
                    self.prefixed('{}:{}'.format(key, sort_key))
                )
        return self.redis_server.set(self.prefixed(
            '{}:{}'.format(key, sort_key)), value)

    def delete(self, key, sort_key):
        if sort_key is not None:
            self.redis_server.zrem(self.prefixed(key), sort_key)
        prev_value = self.get(key, sort_key)
        prev_obj = None
        if prev_value is not None:
            prev_obj = json.loads(prev_value)
        for sec_index in self._secondary_indexes:
            if (prev_obj is not None and
                    sec_index in prev_obj.keys()):
                self.redis_server.srem(
                    self.prefixed('secondary_indexes:{}:{}'.format(
                        sec_index, prev_obj[sec_index]
                    )),
                    self.prefixed('{}:{}'.format(key, sort_key))
                )
        return self.redis_server.delete(self.prefixed(
            '{}:{}'.format(key, sort_key)))

    def history(self, key, _from='-', _to='+', _desc=True):
        if _from != '-':
            _from = '({}'.format(_from)
        if _to != '+':
            _to = '({}'.format(_to)
        res = [self.get(key, kid.decode('utf8'))
               for kid in self.redis_server.zrevrangebylex(
                   self.prefixed(key),
                   _to, _from,
                   start=0, num=100)]
        if not _desc:
            return res[::-1]
        return res

    def latest(self, key):
        res = self.redis_server.zrevrangebylex(
            self.prefixed(key),
            '+', '-',
            start=0, num=1
        )
        if len(res) > 0:
            return self.get(key, res[0].decode('utf8'))
        else:
            return None

    def transaction(self, func, *watchs, **params):
        return self.redis_server.transaction(func, *watchs, **params)

    def find(self, index, value):
        keys = self.redis_server.smembers(
            self.prefixed('secondary_indexes:{}:{}'.format(
                index, value
            ))
        )
        if keys is not None:
            return {
                'count': len(keys),
                'items': [self.redis_server.get(key.decode('utf-8'))
                          for key in keys]
            }
        return {'count': 0, 'items': []}
