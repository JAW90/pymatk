import re
import time
import configparser
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

# ============================================================================
# Command Classes (Command Pattern)
# ============================================================================


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

        print(f"Loop complete\n")

    def __repr__(self):
        return f"LoopCommand({self.variable_name} in {self.values}, {len(self.body)} commands)"


# ============================================================================
# Execution Context
# ============================================================================


class ExecutionContext:
    """Maintains state during sequence execution"""

    def __init__(self, rack):
        self.rack = rack
        self.variables = {}
        self.data = []
        self.logs = []

    def set_variable(self, name: str, value: Any):
        """Set a variable that can be used in commands"""
        self.variables[name] = value

    def get_variable(self, name: str) -> Any:
        """Get a variable value"""
        return self.variables.get(name)

    def resolve_variable(self, value: Any) -> Any:
        """Resolve variable references like $temperature"""
        if isinstance(value, str) and value.startswith("$"):
            var_name = value[1:]
            if var_name in self.variables:
                return self.variables[var_name]
            else:
                raise ValueError(f"Undefined variable: {var_name}")
        return value

    def add_data(self, reading: Dict):
        """Add a data reading"""
        self.data.append(reading)

    def log(self, message: str):
        """Add a log message"""
        self.logs.append({"timestamp": time.time(), "message": message})

    def save_data(self, filename: str):
        """Save collected data to CSV"""
        import csv

        if not self.data:
            print("No data to save")
            return

        with open(filename, "w", newline="") as f:
            fieldnames = self.data[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.data)

        print(f"Saved {len(self.data)} data points to {filename}")


# ============================================================================
# Sequence Parser
# ============================================================================


class SequenceParser:
    """Parse INI-style sequence files into Command objects"""

    def __init__(self):
        self.commands = []
        self.metadata = {}

    def parse_file(self, filepath: str) -> List[Command]:
        """Parse a sequence file and return list of commands"""

        with open(filepath, "r") as f:
            lines = f.readlines()

        # Parse sections manually
        current_section = None
        sequence_lines = []

        for line in lines:
            stripped = line.strip()

            # Check for section headers
            if stripped.startswith("[") and stripped.endswith("]"):
                current_section = stripped[1:-1]
                continue

            # Store EXPERIMENT metadata
            if current_section == "EXPERIMENT" and "=" in stripped:
                key, value = stripped.split("=", 1)
                self.metadata[key.strip()] = value.strip()

            # Collect SEQUENCE lines
            elif current_section == "SEQUENCE":
                sequence_lines.append(line.rstrip())

        # Parse the sequence lines into commands
        self.commands = self._parse_lines(sequence_lines)
        return self.commands

    def _parse_lines(self, lines: List[str], in_loop: bool = False) -> List[Command]:
        """Parse lines into commands"""
        commands = []
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Skip empty lines and comments
            if not line or line.startswith("#"):
                i += 1
                continue

            # Check for END (loop terminator) - case insensitive
            if line.upper() == "END":
                if in_loop:
                    # End of loop body - we're done
                    return commands
                else:
                    raise ValueError("END without matching LOOP")

            # Parse the command
            result = self._parse_command(line, lines, i)

            if isinstance(result, tuple):
                # It's a loop - result is (LoopCommand, lines_consumed)
                commands.append(result[0])
                i += result[1]
            else:
                commands.append(result)
                i += 1

        # If we're in a loop and reach here, we didn't find END
        if in_loop:
            raise ValueError("LOOP without matching END")

        return commands

    def _parse_command(self, line: str, all_lines: List[str], current_index: int):
        """Parse a single command line"""

        # Store original line for error messages
        original_line = line

        # Normalize command keywords to uppercase for parsing
        # But preserve values (especially string values and variable names)
        parts = line.split(None, 1)  # Split on first whitespace
        if parts:
            command_keyword = parts[0].upper()
            rest_of_line = parts[1] if len(parts) > 1 else ""

            # For commands with parameters, normalize parameter names too
            if command_keyword in ["WAIT_STABLE", "RECORD"]:
                # Normalize parameter names like tolerance=, timeout=, duration=, interval=
                rest_of_line = re.sub(
                    r"\b(tolerance|TOLERANCE)\b", "TOLERANCE", rest_of_line, flags=re.IGNORECASE
                )
                rest_of_line = re.sub(
                    r"\b(timeout|TIMEOUT)\b", "TIMEOUT", rest_of_line, flags=re.IGNORECASE
                )
                rest_of_line = re.sub(
                    r"\b(duration|DURATION)\b", "DURATION", rest_of_line, flags=re.IGNORECASE
                )
                rest_of_line = re.sub(
                    r"\b(interval|INTERVAL)\b", "INTERVAL", rest_of_line, flags=re.IGNORECASE
                )

            line = f"{command_keyword} {rest_of_line}" if rest_of_line else command_keyword

        # INIT command
        if line.startswith("INIT "):
            instrument = line[5:].strip()
            return InitCommand(instrument)

        # SET command
        if line.startswith("SET "):
            match = re.match(r"SET\s+(\w+)\.(\w+)\s*=\s*(.+)", line)
            if match:
                instrument, parameter, value = match.groups()
                value = value.strip()
                # Try to convert to number if it's not a variable
                if not value.startswith("$"):
                    try:
                        value = float(value) if "." in value else int(value)
                    except ValueError:
                        pass  # Keep as string
                return SetCommand(instrument, parameter, value)

        # WAIT command (simple duration)
        if line.startswith("WAIT ") and not line.startswith("WAIT_STABLE"):
            rest = line[5:].strip()
            duration = float(rest)
            return WaitCommand(duration)

        # WAIT_STABLE command
        if line.startswith("WAIT_STABLE "):
            match = re.match(
                r"WAIT_STABLE\s+(\w+)\.(\w+)\s+TOLERANCE=([\d.]+)\s+TIMEOUT=([\d.]+)", line
            )
            if match:
                instrument, parameter, tolerance, timeout = match.groups()
                return WaitStableCommand(instrument, parameter, float(tolerance), float(timeout))
            else:
                raise ValueError(f"Invalid WAIT_STABLE syntax: {original_line}")

        # RECORD command
        if line.startswith("RECORD "):
            match = re.match(r"RECORD\s+([\w,\s]+)\s+DURATION=([\d.]+)\s+INTERVAL=([\d.]+)", line)
            if match:
                instruments_str, duration, interval = match.groups()
                instruments = [x.strip() for x in instruments_str.split(",")]
                return RecordCommand(instruments, float(duration), float(interval))
            else:
                raise ValueError(f"Invalid RECORD syntax: {original_line}")

        # LOG command
        if line.startswith("LOG "):
            message = line[4:].strip().strip("\"'")
            return LogCommand(message)

        # SAVE_DATA command
        if line.startswith("SAVE_DATA "):
            filename = line[10:].strip()
            return SaveDataCommand(filename)

        # LOOP command (in _parse_command method)
        if line.startswith("LOOP "):
            match = re.match(r"LOOP\s+(\w+)\s+IN\s+(.+)", line)
            if match:
                var_name, values_str = match.groups()
                # Parse comma-separated values
                values = [x.strip() for x in values_str.split(",")]
                # Try to convert to numbers
                parsed_values = []
                for v in values:
                    try:
                        parsed_values.append(float(v) if "." in v else int(v))
                    except ValueError:
                        parsed_values.append(v)

                # Find the loop body (until matching END)
                body_lines = []
                j = current_index + 1
                indent_level = 0

                while j < len(all_lines):
                    body_line = all_lines[j].strip()
                    body_line_upper = body_line.upper()

                    # Check if this is a nested LOOP
                    if body_line_upper.startswith("LOOP "):
                        # Nested loop found, increase indent level
                        indent_level += 1
                        body_lines.append(all_lines[j])
                    elif body_line_upper == "END":
                        if indent_level == 0:
                            # This END matches our LOOP - don't include it in body
                            break
                        else:
                            # This END belongs to a nested loop
                            indent_level -= 1
                            body_lines.append(all_lines[j])
                    elif body_line:  # Only add non-empty lines
                        body_lines.append(all_lines[j])
                    # Empty lines and comments are preserved as-is
                    elif not body_line or body_line.startswith("#"):
                        body_lines.append(all_lines[j])

                    j += 1

                if j >= len(all_lines):
                    raise ValueError(f"LOOP at line {current_index} has no matching END")

                # Parse the body recursively
                print(f"DEBUG: Parsing loop body with {len(body_lines)} lines:")
                for idx, bl in enumerate(body_lines):
                    print(f"  {idx}: '{bl.strip()}'")
                # body_commands = self._parse_lines(body_lines, in_loop=True)
                body_commands = self._parse_lines(body_lines, in_loop=False)

                # Return the loop command and number of lines consumed (including the END)
                lines_consumed = j - current_index + 1  # +1 to skip past the END
                return (LoopCommand(var_name, parsed_values, body_commands), lines_consumed)
            else:
                raise ValueError(f"Invalid LOOP syntax: {original_line}")


# ============================================================================
# Sequence Executor
# ============================================================================


class SequenceExecutor:
    """Execute a sequence of commands"""

    def __init__(self, rack):
        self.rack = rack
        self.context = ExecutionContext(rack)
        self.commands = []

    def load_sequence(self, filepath: str):
        """Load a sequence from file"""
        parser = SequenceParser()
        self.commands = parser.parse_file(filepath)
        print(f"Loaded {len(self.commands)} top-level commands from {filepath}")

    def run(self, dry_run: bool = False):
        """Execute the loaded sequence"""
        if dry_run:
            print("=== DRY RUN MODE ===")
            self._print_commands(self.commands)
            return

        print("=== STARTING SEQUENCE EXECUTION ===\n")

        try:
            for command in self.commands:
                command.execute(self.context)
        except Exception as e:
            print(f"\n!!! EXECUTION FAILED !!!")
            print(f"Error: {e}")
            raise

        print("\n=== SEQUENCE EXECUTION COMPLETE ===")

    def _print_commands(self, commands: List[Command], indent: int = 0):
        """Print commands in a readable format (for dry run)"""
        for cmd in commands:
            print("  " * indent + str(cmd))
            if isinstance(cmd, LoopCommand):
                self._print_commands(cmd.body, indent + 1)


# ============================================================================
# Example Usage
# ============================================================================


# Mock instrument classes for demonstration
class MockInstrument:
    def __init__(self, name):
        self.name = name
        self.parameters = {}

    def initialize(self):
        print(f"  [{self.name}] Initialized")

    def set_parameter(self, param, value):
        self.parameters[param] = value
        print(f"  [{self.name}] {param} set to {value}")

    def get_parameter(self, param):
        return self.parameters.get(param, 0)

    def read_value(self):
        import random

        return random.uniform(20, 30)


class MockInstrumentRack:
    def __init__(self):
        self.instruments = {}

    def add_instrument(self, name, instrument):
        self.instruments[name] = instrument

    def get_instrument(self, name):
        return self.instruments.get(name)


if __name__ == "__main__":
    # Create mock instrument rack
    rack = MockInstrumentRack()
    rack.add_instrument("temperature_controller", MockInstrument("TempController"))
    rack.add_instrument("sensor1", MockInstrument("Sensor1"))
    rack.add_instrument("sensor2", MockInstrument("Sensor2"))

    # Create executor and load sequence
    executor = SequenceExecutor(rack)
    executor.load_sequence("experiment_sequence.ini")

    # Show what would be executed (dry run)
    print("\n" + "=" * 60)
    executor.run(dry_run=True)

    # Actually execute
    print("\n" + "=" * 60)
    executor.run(dry_run=False)
