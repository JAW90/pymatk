import numpy as np

from simple_pid import PID
from simple_pid.pid import _clamp
from typing import Tuple


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
        sample_time: float = 0.01,
        starting_output: float = 0.2,
        output_limits: Tuple[float, float] = (0, 100),
        deadband: float = 0.2,
        output_rate_limit: float | None = None,
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
        self.output_rate_limit = output_rate_limit

        try:
            assert output_limits[0] < output_limits[1]
        except AssertionError:
            raise ValueError(
                f"""Output lower limit {output_limits[0]} must be less than
                  upper limit {output_limits[1]}."""
            )

    def _is_in_deadband(self, input):
        if np.abs(input - self.setpoint) < self.deadband:
            return True
        else:
            return False

    def _limit_rate(self, new_output: float, last_output: float):
        if np.abs(last_output - new_output) > self.output_rate_limit:
            return last_output - self.output_rate_limit * np.sign(
                last_output - new_output
            )
        else:
            return new_output

    def __call__(self, input_: float, dt: float | None = None) -> float | None:
        # Check if current measurement is within deadband of setpoint
        if self._is_in_deadband(input=input_) and (
            self._last_output is not None
        ):
            # If in deadband, get last output
            return self._last_output
        else:
            # If not, get new output
            last_output = self._last_output
            new_output = super().__call__(input_, dt)

            # If output is rate limited, and new output is finite and last
            # output is not none
            if (
                self.output_rate_limit is not None
                and new_output is not None
                and last_output is not None
            ):
                new_output = self._limit_rate(new_output, last_output)
                new_output = _clamp(new_output, self.output_limits)

            self._last_output = new_output
            return new_output
