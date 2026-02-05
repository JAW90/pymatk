import time


class TimeKeeper:
    def __init__(self):
        self.start_time = time.time()

    @property
    def elapsed_time(self) -> float:
        time_now = time.time()
        return time_now - self.start_time

    def unix_time(self) -> float:
        return time.time()

    def restart(self):
        self.start_time = time.time()
