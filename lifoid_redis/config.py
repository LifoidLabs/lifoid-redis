# -*- coding: utf8 -*-
"""
Redis plugin configuration
Author: Romary Dupuis <romary@me.com>
"""
from lifoid.config import Configuration, environ_setting


class RedisConfiguration(Configuration):
    """
    Redis configuration
    """
    host = environ_setting('REDIS_HOST', '127.0.0.1', required=False)
    port = environ_setting('REDIS_PORT', 6379, required=False)
    db = environ_setting('REDIS_DB', 0, required=False)
