from typing import Any, Callable

from loguru import logger
from paho.mqtt import client

from transport_sequencing import common


class MqttClient:
    def __init__(self, client_id: str = "") -> None:
        self._client = client.Client(client_id=client_id)
        self.connect()
        self.enable_logging()

    def connect(self) -> None:
        self._client.connect(
            host=common.MQTT_HOST,
            port=common.MQTT_PORT,
        )

    def enable_logging(self) -> None:
        def on_log(client, userdata, level, buf):
            logger.debug(buf)

        self._client.on_log = on_log

    def disable_logging(self) -> None:
        self._client.on_log = None

    def set_on_message(self, func: Callable) -> None:
        self._client.on_message = func

    def publish(self, topic: str, payload: Any, qos: int = 0) -> None:
        self._client.publish(
            topic=topic,
            payload=str(payload),
            qos=qos,
        )

    def subscribe(self, topic: str) -> None:
        self._client.subscribe(topic=topic)

    def loop_forever(self) -> None:
        self._client.loop_forever()

    def loop_stop(self) -> None:
        self._client.loop_stop()

    def disconnect(self) -> None:
        self._client.disconnect()
