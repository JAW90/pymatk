import random
from typing import Tuple


class RandomGenerator:
    @property
    def new_random_number(self) -> float:
        return random.random()

    def get_random_number(self) -> float:
        return random.random()

    @property
    def two_random_numbers(self) -> Tuple[float, float]:
        return (random.random(), random.random())

    def get_two_random_numbers(self) -> Tuple[float, float]:
        return (random.random(), random.random())
