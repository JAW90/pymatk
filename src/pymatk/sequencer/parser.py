import re

from typing import List

from pymatk.sequencer import (
    Command,
    LogCommand,
    SetCommand,
    InitCommand,
    LoopCommand,
    WaitCommand,
    RecordCommand,
    SaveDataCommand,
    WaitStableCommand,
)


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
