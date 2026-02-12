import threading
import time
import tomllib

from pymatk.config_parser import ConfigParser
from pymatk.data_writer import DataWriter
from pymatk.instruments import InstrumentRack

# TODO: Implement logging and debugging


# TODO: Add docstrings


class SimpleManager:
    """
    SimpleManager: loads a config file, loads instruments, configures variables,
    createa a datafile and, optionally, starts a thread to collect data indefinitely.
    """

    def __init__(
        self,
        description,
        config_file: str,
        update_time: float = 0.25,
        running: bool = True,
    ):
        self.description = description
        self._running = running
        self._update_time = update_time

        if not config_file.endswith(".toml"):
            raise FileNotFoundError("Not a valid .toml configuration file.")

        try:
            with open(config_file, "rb") as f:
                self._config = tomllib.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {config_file}")

        self.cfg_parser = ConfigParser(self.description, self._config)

        self._instrument_rack = InstrumentRack(
            self.description, self.cfg_parser.parse_instrument_configurations()
        )

        self._data_writer = DataWriter(
            *self.cfg_parser.parse_data_config(),
            self._instrument_rack.get_variable_names(units=True),
        )

        self.cfg_parser.parse_controller_configuration()

        # self._instrument_rack.instantiate_instruments()
        # self._instrument_rack.apply_initial_settings()
        # self._instrument_rack.configure_variables()

        self._thread = threading.Thread(target=self._main_loop, daemon=True)

        if self._running:
            self._data_writer.create_new_file()
            self._thread.start()

    @property
    def instrument_rack(self):
        return self._instrument_rack

    def start(self):
        self._running = True
        self._data_writer.create_new_file()
        self._thread.start()

    def stop(self):
        self._running = False

    def _main_loop(self):
        while self._running:
            self._instrument_rack.read_instruments()
            self._data_writer.write_data(self._instrument_rack.readings)
            time.sleep(self._update_time)
