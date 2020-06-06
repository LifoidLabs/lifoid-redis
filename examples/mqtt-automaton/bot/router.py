from bot.actions import (greeting, user_name,
                           query_temperature,
                           temperature_change,
                           fallback,
                           MQTTChatbot)


actions = [
    greeting,
    user_name,
    query_temperature,
    temperature_change,
    fallback
]

bot_model = MQTTChatbot
