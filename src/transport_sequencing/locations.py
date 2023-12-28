from random import uniform

from haversine import haversine

from transport_sequencing.models import Coords


def get_random_coord():
    min_lng = 53.515001
    min_lat = 9.7270200
    max_lng = 53.701639
    max_lat = 10.271530
    val1 = uniform(min_lng, max_lng)
    val2 = uniform(min_lat, max_lat)
    return Coords(val1, val2)


def get_distance_between_coords(p1: Coords, p2: Coords) -> float:
    return haversine(p1.as_tuple(), p2.as_tuple())
