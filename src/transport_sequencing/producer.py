import asyncio
from queue import SimpleQueue
from random import randrange

from loguru import logger

from transport_sequencing import models, transporter


class CargoProducer:
    def __init__(
        self,
        queue: SimpleQueue,
        speed: int = 1,
    ) -> None:
        self._task: asyncio.Task
        self._speed = speed
        self._queue = queue
        self.enabled = asyncio.Event()
        self.done = asyncio.Event()

    async def produce(self) -> None:
        self.enabled.set()
        t_id = 0
        while self.enabled.is_set():
            new_transporter = transporter.Transporter(
                transporter_id=t_id,
                max_fuel=models.Fuel(value=randrange(60, 120, 10)),
                max_payload=models.Payload(value=randrange(1000, 10000, 100)),
                max_speed=models.Speed(value=randrange(80, 120, 10)),
            )
            self._queue.put(new_transporter)
            t_id += 1
            logger.debug("Added transporter")
            await asyncio.sleep(randrange(0, 100, 1) / self._speed)

    def start(self) -> asyncio.Task:
        logger.debug("starting")
        eventloop = asyncio.get_event_loop()
        self._task = eventloop.create_task(self.produce())
        return self._task

    async def stop(self) -> None:
        logger.debug("stopping")
        self.enabled.clear()
        await self._task
        self.done.set()
