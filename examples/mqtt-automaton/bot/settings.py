import os

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
ROUTER_CONF = 'bot.router'
TEMPLATES_PATH = os.path.join(PROJECT_ROOT, 'templates')
TRANSLATIONS_PATH = os.path.join(PROJECT_ROOT, 'translations')
TESTS_PATH = os.path.join(PROJECT_ROOT, 'tests')
PLUGIN_PATHS = []
PLUGINS = [
    'lifoid.client_auth',
    'lifoid_redis'
]
