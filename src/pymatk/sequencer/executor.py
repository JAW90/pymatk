from typing import List

from pymatk.managers import ExecutionContext
from pymatk.sequencer import SequenceParser, Command, LoopCommand


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
            print("\n!!! EXECUTION FAILED !!!")
            print(f"Error: {e}")
            raise

        print("\n=== SEQUENCE EXECUTION COMPLETE ===")

    def _print_commands(self, commands: List[Command], indent: int = 0):
        """Print commands in a readable format (for dry run)"""
        for cmd in commands:
            print("  " * indent + str(cmd))
            if isinstance(cmd, LoopCommand):
                self._print_commands(cmd.body, indent + 1)
