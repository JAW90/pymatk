import random
from typing import Tuple


class RandomGenerator:
    def __init__(self):
        self._param = 6

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

    @property
    def param(self):
        return self._param

    @param.setter
    def param(self, new_param):
        self._param = new_param

    def get_param(self):
        return self._param

    def set_param(self, new_param):
        self._param = new_param
