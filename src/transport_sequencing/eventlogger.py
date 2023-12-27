import asyncio

from loguru import logger
from paho.mqtt.client import MQTTMessage

from transport_sequencing import mqtt_client


class TopicLogger:
    def __init__(
        self,
        topic: str,
        stop_event: asyncio.Event | None = None,
        enable_logging: bool = False,
    ) -> None:
        self._stop_event = stop_event
        self._mqtt_client = mqtt_client.MqttClient(client_id="EventLogger")
        if enable_logging:
            self._mqtt_client.enable_logging()
        self._mqtt_client.subscribe(topic=topic)
        if stop_event is not None:
            self._auto_stop()

    def _auto_stop(self) -> None:
        async def _wait_for_stop():
            await self._stop_event.wait()
            self.stop()

        eventloop = asyncio.get_event_loop()
        eventloop.create_task(_wait_for_stop())

    def _run_loop(self) -> None:
        def on_message(client, userdata, msg: MQTTMessage):
            logger.info(f"{msg.topic} - {msg.payload}")

        self._mqtt_client.set_on_message(on_message)
        self._mqtt_client.loop_forever()

    def start(self) -> asyncio.Future:
        eventloop = asyncio.get_event_loop()
        return eventloop.run_in_executor(None, self._run_loop)

    def stop(self) -> None:
        logger.debug("stopping")
        self._mqtt_client.loop_stop()
        self._mqtt_client.disconnect()

    def disable_logging(self) -> None:
        self._mqtt_client.disable_logging()
