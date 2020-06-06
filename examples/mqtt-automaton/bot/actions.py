from collections import namedtuple
import datetime
from lifoid.data.record import NamedtupleRecord
from lifoid.data.memory import DictBackend
from lifoid.action import action
from lifoid.views import render_view
from lifoid.automaton import Automaton
from lifoid.data.repository import Repository
from lifoid.message.message_types import CHAT, M2M
from lifoid.config import settings
from lifoid_redis.backend import RedisBackend


STATES = ['ready', 'ask_name']
TRANSITIONS = [
    {
        'trigger': 'greeting', 'source': 'ready',
        'dest': '=',
        'unless': 'user_unknown',
        'after': 'say_hello'
    },
    {
        'trigger': 'greeting', 'source': 'ready',
        'dest': 'ask_name',
        'conditions': ['user_unknown'],
        'after': ['say_hello', 'ask_name']
    },
    {
        'trigger': 'user_name', 'source': 'ask_name',
        'dest': 'ready',
        'after': ['store_name', 'say_hello']
    },
    {
        'trigger': 'unknown', 'source': 'ask_name',
        'dest': '=',
        'conditions': ['ask_name_counter'],
        'after': ['ask_name']
    },
    {
        'trigger': 'temperature_change', 'source': '*',
        'dest': '=',
        'after': ['set_temperature']
    },
    {
        'trigger': 'query_temperature', 'source': '*',
        'dest': '=',
        'after': ['get_temperature']
    },
    {
        'trigger': 'unknown', 'source': '*',
        'dest': 'ready',
        'after': ['dont_understand']
    }
]


SENSOR_DATA_FIELDS = ['value']


class SensorData(namedtuple('SensorData', SENSOR_DATA_FIELDS),
                 NamedtupleRecord):
    """
    Example of namedtuple based record
    """
    def __new__(cls, **kwargs):
        default = {f: None for f in SENSOR_DATA_FIELDS}
        default.update(kwargs)
        return super(SensorData, cls).__new__(cls, **default)


class SensorDataRepository(Repository):
    """
    A place to store our sensors information
    """
    klass = SensorData


class MQTTChatbot(Automaton):
    """
    Example of automaton based MQTT Bot
    """
    def __init__(self, lifoid_id):
        self.states = STATES
        self.transitions = TRANSITIONS
        self.initial = 'ready'
        self.sensor_data = SensorDataRepository(RedisBackend,
                                                'sensor-data')
        super(MQTTChatbot, self).__init__(lifoid_id)

    def user_unknown(self, _render, _message):
        return self.get('name', None) is None

    def store_name(self, _render, message):
        parsed_message = message.payload.text.split(' ')
        self['name'] = parsed_message[-1]
        return True

    def say_hello(self, render, _message):
        self['ask_name_counter'] = 0
        return render_view(render, 'hello.yml', context=self)

    def ask_name(self, render, _message):
        self['ask_name_counter'] += 1
        return render_view(render, 'ask_name.yml', context=self)

    def set_temperature(self, _, message):
        data = SensorData(value=float(message.payload))
        data_timestamp = datetime.datetime.utcnow().isoformat()[:-3]
        self.sensor_data.save('temperature', data_timestamp, data)

    def get_temperature(self, render, _message):
        data = self.sensor_data.latest('temperature')
        if data is None:
            return render_view(render, 'dont_know.yml')
        return render_view(render, 'give_temperature.yml', context=data.value)

    def ask_name_counter(self, _render, _message):
        return bool(self['ask_name_counter'] < 4)

    def dont_understand(self, render, _message):
        return render_view(render, 'dont_understand.yml', context=self)


@action(lambda message, _: message.message_type == CHAT and
        'hello' in message.payload.text.lower())
def greeting(render, message, mqtt_bot):
    mqtt_bot.greeting(render, message)


@action(lambda message, _: message.message_type == CHAT and
        message.from_user != message.lifoid_id and
        'name' in message.payload.text)
def user_name(render, message, mqtt_bot):
    mqtt_bot.user_name(render, message)


@action(lambda message, _: message.message_type == CHAT and
        message.from_user != message.lifoid_id and
        'temperature' in message.payload.text)
def query_temperature(render, message, mqtt_bot):
    mqtt_bot.query_temperature(render, message)


@action(lambda message, _:
        message.message_type == M2M and
        'temperature' in message.topic)
def temperature_change(render, message, mqtt_bot):
    mqtt_bot.temperature_change(render, message)


@action()
def fallback(render, message, mqtt_bot):
    mqtt_bot.unknown(render, message)
