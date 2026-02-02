import numpy as np
import time

from simple_pid import PID
from threading import Thread


class PIDController(PID):
    """
    Docstring for PIDController
    """

    def __init__(
        self,
        Kp: float = 2,
        Ki: float = 0.05,
        Kd: float = 0,
        setpoint: float = 6,
        sample_time=0.01,
        starting_output: float = 0.2,
        output_limits: tuple = (0, 100),
        deadband: float = 0.2,
        output_rate: float = 0.05,
        **kwargs,
    ):
        super().__init__(
            Kp=Kp,
            Ki=Ki,
            Kd=Kd,
            setpoint=setpoint,
            sample_time=sample_time,
            output_limits=output_limits,
            starting_output=starting_output,
            **kwargs,
        )

        self.deadband = deadband
        self.output_rate = output_rate
        self.last_output = None

    def is_in_deadband(self, input):
        if np.abs(input - self.setpoint) < self.deadband:
            return True
        else:
            return False
        
    def rate_limit(self, input):
        pass

    def __call__(self, input_: float, dt: float | None = None) -> float | None:
        if self.is_in_deadband(input=input_) and (
            self.last_output is not None
        ):
            return self.last_output
        else:
            new_output = super().__call__(input_, dt)

            pass


class Foo:
    def __init__(self):
        self._last = 42


class Bar(Foo):
    def __init__(self):
        super().__init__()

    def do_something(self):
        print(self._last)


class PIDControllerOld:
    """
    Docstring for PIDController
    """

    def __init__(
        self,
        P: float = 2,
        I: float = 0.05,
        D: float = 0,
        setpoint: float = 6,
        deadband: float = 0.2,
        starting_output: float = 21,
        rate: float = 0.05,
        wait_time: float = 0.25,
    ):
        self.setpoint = setpoint
        self.deadband = deadband
        self.pid = PID(
            P, I, D, setpoint=setpoint, starting_output=starting_output
        )
        self.wait_time = wait_time
        self.new_data = False
        self.control = starting_output
        self.rate = rate
        self.thread = Thread(target=self.PIDLoop, daemon=True)
        self.thread.start()

    def set_P(self, P):
        self.pid.Kp = P

    def set_I(self, I):
        self.pid.Ki = I

    def set_D(self, D):
        self.pid.Kd = D

    def set_setpoint(self, setpoint):
        self.pid.setpoint = setpoint

    @property
    def P(self):
        return self.pid.Kp

    @P.setter
    def P(self, P):
        self.pid.Kp = P

    @property
    def I(self):
        return self.pid.Ki

    @I.setter
    def I(self, I):
        self.pid.Ki = I

    def get_P(self):
        return self.pid.Kp

    def get_I(self):
        return self.pid.Ki

    def get_D(self):
        return self.pid.Kd

    def get_setpoint(self):
        return self.pid.setpoint

    def get_control(self):
        return self.control

    def update(self, data: float):
        self.data = data
        self.new_data = True

    def reset(self):
        self.pid.reset()

    def PIDLoop(self):
        while True:
            if self.new_data:
                p = self.data
                old_control = self.control
                if np.abs(p - self.pid.setpoint) > self.deadband:
                    self.control = self.pid(p) or 0
                else:
                    self.rate = 0.5
                if self.control >= 100:
                    self.control = 100
                if self.control < 0:
                    self.control = 0
                if np.abs(old_control - self.control) > self.rate:
                    self.control = old_control - self.rate * np.sign(
                        old_control - self.control
                    )
                self.new_data = False
            time.sleep(self.wait_time)
