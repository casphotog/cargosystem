#!/usr/bin/env python3

import asyncio
import sys
from queue import SimpleQueue

from loguru import logger

from transport_sequencing import common
from transport_sequencing.eventlogger import TopicLogger
from transport_sequencing.producer import CargoProducer

LOG_LEVEL = "DEBUG"


def configure_logging():
    logger.remove()
    logger.add(
        sink=sys.stderr,
        colorize=True,
        level=LOG_LEVEL,
    )


async def main():
    queue = SimpleQueue()
    producer = CargoProducer(queue, 20)
    eventlogger = TopicLogger(
        topic=common.MQTT_TOPIC_NEW_TRANSPORTER,
        stop_event=producer.done,
    )
    eventlogger_task = eventlogger.start()
    producer.start()
    await asyncio.sleep(10)
    await producer.stop()
    await eventlogger_task


if __name__ == "__main__":
    configure_logging()
    asyncio.run(main())
