# Mock instrument classes for demonstration
from pymatk.sequencer import SequenceExecutor


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
