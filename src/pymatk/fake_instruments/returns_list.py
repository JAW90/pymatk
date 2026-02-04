import time
import random


class ReturnsList:
    @property
    def data(self):
        timenow = time.time()
        random_number = random.random()
        return [timenow, random_number]
