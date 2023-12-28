import math

from transport_sequencing import locations
from transport_sequencing.models import Coords


class CargoConsumer:
    def __init__(self) -> None:
        self._location = locations.get_random_coord()

    def is_close_to(self, radius: int):
        pass
