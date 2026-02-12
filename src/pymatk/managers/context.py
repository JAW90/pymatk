import time

from typing import Any, Dict


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
