import time

from abc import ABC, abstractmethod
from typing import Any, List

from pymatk import ExecutionContext


class Command(ABC):
    """Base class for all sequence commands"""

    @abstractmethod
    def execute(self, context: "ExecutionContext"):
        """Execute the command"""
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}()"


class InitCommand(Command):
    """Initialize an instrument"""

    def __init__(self, instrument_name: str):
        self.instrument_name = instrument_name

    def execute(self, context: "ExecutionContext"):
        instrument = context.rack.get_instrument(self.instrument_name)
        if instrument:
            print(f"Initializing {self.instrument_name}...")
            instrument.initialize()
        else:
            raise ValueError(f"Instrument '{self.instrument_name}' not found in rack")

    def __repr__(self):
        return f"InitCommand({self.instrument_name})"


class SetCommand(Command):
    """Set an instrument parameter"""

    def __init__(self, instrument_name: str, parameter: str, value: Any):
        self.instrument_name = instrument_name
        self.parameter = parameter
        self.value = value

    def execute(self, context: "ExecutionContext"):
        # Resolve variables (e.g., $temperature)
        resolved_value = context.resolve_variable(self.value)

        instrument = context.rack.get_instrument(self.instrument_name)
        if instrument:
            print(f"Setting {self.instrument_name}.{self.parameter} = {resolved_value}")
            instrument.set_parameter(self.parameter, resolved_value)
        else:
            raise ValueError(f"Instrument '{self.instrument_name}' not found")

    def __repr__(self):
        return f"SetCommand({self.instrument_name}.{self.parameter} = {self.value})"


class WaitCommand(Command):
    """Wait for a specified duration (in seconds)"""

    def __init__(self, duration: float):
        self.duration = duration

    def execute(self, context: "ExecutionContext"):
        print(f"Waiting for {self.duration} seconds...")
        time.sleep(self.duration)

    def __repr__(self):
        return f"WaitCommand({self.duration}s)"


class WaitStableCommand(Command):
    """Wait until a parameter is stable within tolerance"""

    def __init__(self, instrument_name: str, parameter: str, tolerance: float, timeout: float):
        self.instrument_name = instrument_name
        self.parameter = parameter
        self.tolerance = tolerance
        self.timeout = timeout

    def execute(self, context: "ExecutionContext"):
        instrument = context.rack.get_instrument(self.instrument_name)
        if not instrument:
            raise ValueError(f"Instrument '{self.instrument_name}' not found")

        print(
            f"Waiting for {self.instrument_name}.{self.parameter} to stabilize "
            f"(tolerance={self.tolerance}, timeout={self.timeout}s)..."
        )

        start_time = time.time()
        stable_count = 0
        required_stable_readings = 5
        last_value = None

        while time.time() - start_time < self.timeout:
            current_value = instrument.get_parameter(self.parameter)

            if last_value is not None:
                if abs(current_value - last_value) <= self.tolerance:
                    stable_count += 1
                    if stable_count >= required_stable_readings:
                        print(f"  Stabilized at {current_value}")
                        return
                else:
                    stable_count = 0

            last_value = current_value
            time.sleep(1)

        raise TimeoutError(f"Parameter did not stabilize within {self.timeout}s")

    def __repr__(self):
        return f"WaitStableCommand({self.instrument_name}.{self.parameter})"


class RecordCommand(Command):
    """Record data from instruments"""

    def __init__(self, instrument_names: List[str], duration: float, interval: float):
        self.instrument_names = instrument_names
        self.duration = duration
        self.interval = interval

    def execute(self, context: "ExecutionContext"):
        print(
            f"Recording from {', '.join(self.instrument_names)} "
            f"for {self.duration}s at {self.interval}s intervals..."
        )

        start_time = time.time()
        readings = []

        while time.time() - start_time < self.duration:
            timestamp = time.time()
            reading = {"timestamp": timestamp}

            for inst_name in self.instrument_names:
                instrument = context.rack.get_instrument(inst_name)
                if instrument:
                    reading[inst_name] = instrument.read_value()

            readings.append(reading)
            context.add_data(reading)
            time.sleep(self.interval)

        print(f"  Recorded {len(readings)} data points")

    def __repr__(self):
        return f"RecordCommand({self.instrument_names})"


class LogCommand(Command):
    """Log a message"""

    def __init__(self, message: str):
        self.message = message

    def execute(self, context: "ExecutionContext"):
        resolved_message = context.resolve_variable(self.message)
        print(f"LOG: {resolved_message}")
        context.log(resolved_message)

    def __repr__(self):
        return f"LogCommand({self.message})"


class SaveDataCommand(Command):
    """Save collected data to file"""

    def __init__(self, filename: str):
        self.filename = filename

    def execute(self, context: "ExecutionContext"):
        resolved_filename = context.resolve_variable(self.filename)
        print(f"Saving data to {resolved_filename}...")
        context.save_data(resolved_filename)

    def __repr__(self):
        return f"SaveDataCommand({self.filename})"


class LoopCommand(Command):
    """Loop over values"""

    def __init__(self, variable_name: str, values: List[Any], body: List[Command]):
        self.variable_name = variable_name
        self.values = values
        self.body = body

    def execute(self, context: "ExecutionContext"):
        print(f"Starting loop: {self.variable_name} over {self.values}")

        for value in self.values:
            context.set_variable(self.variable_name, value)
            print(f"\n--- Loop iteration: {self.variable_name} = {value} ---")

            for command in self.body:
                command.execute(context)

        print("Loop complete\n")

    def __repr__(self):
        return f"LoopCommand({self.variable_name} in {self.values}, {len(self.body)} commands)"
