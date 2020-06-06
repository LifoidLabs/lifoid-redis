# Example of Chatbot with temperature sensor

This project structure was initialized with `lifoid init` command.

You can personalize the environment file `.env` according to the
`.env.example` file and specification provided in Lifoid project root.

Make sure there is a MQTT Broker available, e.g. Mosquitto.

Here is an example to launch the bot with a local MQTT broker:

```
lifoid mqtt --host localhost --port 1883 --lifoid_id simple-bot
```

In a separate terminal use `mosquitto_pub` tool to simulate information sent
by a temperature sensor:

```
mosquitto_pub -t temperature -m 27.3
```

Then let's chat with this bot:

```
lifoid chat --host localhost --port 1883 --lifoid_id simple-bot
+-----------------------------------------------------------------------------+
|                                                                             |
|   Lifoid                                                                    |
|                                                                             |
|   Copyright (C) 2017-2018 Romary Dupuis                                     |
|                                                                             |
+-----------------------------------------------------------------------------+


* PLease type in your messages below
hello
from simple-bot --> Hello, what is your name?
My name is Bob
from simple-bot --> Hello Bob
What's the temperature today?
from simple-bot --> Temperature is 27.3
```

