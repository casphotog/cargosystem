from __future__ import annotations

import asyncio

from transport_sequencing import common, locations, mqtt_client
from transport_sequencing.models import Fuel, Payload, Speed


class Transporter:
    def __init__(
        self,
        transporter_id: int,
        max_payload: Payload,
        max_fuel: Fuel,
        max_speed: Speed,
        payload: Payload = Payload(value=0),
        fuel: Fuel = Fuel(value=0),
        speed: Speed = Speed(value=0),
        pub_loc: bool = True,
    ) -> None:
        self._id = transporter_id
        self.location = locations.get_random_coord()
        self._max_payload = max_payload
        self._max_fuel = max_fuel
        self._max_speed = max_speed
        self._payload = payload
        self._fuel = fuel
        self._speed = speed
        self._transporter_client = mqtt_client.MqttClient(
            client_id=f"transporter_{self._id}",
        )
        self._init_mqtt()
        if pub_loc:
            self._publish_location()

    def __repr__(self) -> str:
        return (
            f"id: {self._id}, "
            f"Speed: {self.speed.value}, "
            f"Payload: {self.payload.value}, "
            f"Fuel: {self.fuel.value}, "
            f"Max Speed: {self._max_speed.value}, "
            f"Max Payload: {self._max_payload.value}, "
            f"Max Fuel: {self._max_fuel.value}, "
            f"Location: {self.location}"
        )

    def _init_mqtt(self) -> None:
        self._transporter_client.connect()
        self._transporter_client.publish(
            topic=common.MQTT_TOPIC_NEW_TRANSPORTER,
            payload=str(self),
        )

    def _publish_location(self) -> None:
        async def pub_loc_loop():
            self._transporter_client.publish(
                topic=common.MQTT_TOPIC_LOCATION.format(self._id),
                payload=self.location,
                qos=2,
            )
            await asyncio.sleep(10)

        eventloop = asyncio.get_event_loop()
        eventloop.create_task(pub_loc_loop())

    def load(self, load: Payload | Fuel) -> None:
        if not self.check_capacity(load):
            raise ValueError(f"load {load} exceeds available capacity")
        if isinstance(load, Payload):
            self._payload = self._payload + load
        if isinstance(load, Fuel):
            self._fuel = self._fuel + load

    def check_capacity(self, load: Payload | Fuel) -> bool:
        if isinstance(load, Payload):
            return (self._payload + load) <= self._max_payload
        if isinstance(load, Fuel):
            return (self._fuel + load) <= self._max_fuel
        raise TypeError(f"Unexpected type: {type(load)}")

    @property
    def speed(self) -> Speed:
        return self._speed

    @speed.setter
    def speed(self, speed: Speed) -> None:
        if speed > self._max_speed:
            raise ValueError(
                f"requested speed {speed} exceeds maximum speed {self._max_speed}"
            )
        self._transporter_client.publish(
            topic=common.MQTT_TOPIC_SPEED.format(self._id),
            payload=speed,
        )

    def stop(self) -> None:
        self._speed.value = 0

    @property
    def payload(self) -> Payload:
        return self._payload

    @payload.setter
    def payload(self, payload: Payload) -> None:
        self.load(payload)
        self._transporter_client.publish(
            topic=common.MQTT_TOPIC_PAYLOAD.format(self._id),
            payload=payload,
        )

    @property
    def fuel(self) -> Fuel:
        return self._fuel

    @fuel.setter
    def fuel(self, fuel: Fuel) -> None:
        self.load(fuel)
        self._transporter_client.publish(
            topic=common.MQTT_TOPIC_FUEL.format(self._id),
            payload=fuel,
            qos=2,
        )
