# -*- coding: utf8 -*-
"""
Rasa_nlu plugin for Lifoid
Author: Romary Dupuis <romary@me.com>
"""
from lifoid import signals
from .config import RedisConfiguration
from .backend import RedisBackend

__version__ = '0.1.0'


def get_backend(app):
    return RedisBackend


def get_conf(configuration):
    setattr(configuration, 'redis', RedisConfiguration())


def register():
    signals.get_backend.connect(get_backend)
    signals.get_conf.connect(get_conf)
