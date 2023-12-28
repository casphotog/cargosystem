#!/usr/bin/env python3

import asyncio
import sys
from queue import SimpleQueue

from icecream import ic as debug
from loguru import logger

from transport_sequencing import common, locations
from transport_sequencing.eventlogger import TopicLogger
from transport_sequencing.producer import CargoProducer
from transport_sequencing.transporter import Transporter

LOG_LEVEL_INFO = "INFO"
LOG_LEVEL_DEBUG = "DEBUG"

LOG_LEVEL = LOG_LEVEL_DEBUG


def configure_logging():
    debug.disable()
    logger.remove()
    logger.add(
        sink=sys.stderr,
        colorize=True,
        level=LOG_LEVEL,
    )
    debug.configureOutput("DEBUG | ")
    if LOG_LEVEL == LOG_LEVEL_DEBUG:
        debug.enable()


async def main():
    queue: SimpleQueue[Transporter] = SimpleQueue()
    producer = CargoProducer(queue, 20)
    eventlogger = TopicLogger(
        topic=common.MQTT_TOPIC_NEW_TRANSPORTER,
        stop_event=producer.done,
    )
    eventlogger_task = eventlogger.start()
    producer.start()
    await asyncio.sleep(5)
    t1 = queue.get()
    t2 = queue.get()
    debug(t1.location, t2.location)
    distance = locations.get_distance_between_coords(
        t1.location,
        t2.location,
    )
    debug(distance)
    await producer.stop()
    await eventlogger_task


if __name__ == "__main__":
    configure_logging()
    asyncio.run(main())
