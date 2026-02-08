import threading
import time
import tomllib

from pymatk.config_parser import ConfigParser
from pymatk.data_writer import DataWriter
from pymatk.instruments import InstrumentRack

# TODO: Implement logging and debugging

# TODO: How to start and stop?

# TODO: Add docstrings


class BasicManager:
    """
    BasicManager: loads a config file, loads instruments, configures variables,
    createa a datafile and, optionally, starts a thread to collect data indefinitely.
    """

    def __init__(
        self,
        description,
        config_file: str,
        update_time: float = 0.25,
        running: bool = True,
        debug: bool = False,
    ):
        self.description = description
        self._running = running
        self._update_time = update_time
        self.debug = debug

        if not config_file.endswith(".toml"):
            raise FileNotFoundError("Not a valid .toml configuration file.")

        try:
            with open(config_file, "rb") as f:
                self._config = tomllib.load(f)
        except FileNotFoundError:
            print(f"Config file not found: {config_file}")

        cfg_parser = ConfigParser(self.description, self._config)

        self._instrument_rack = InstrumentRack(
            self.description, cfg_parser.parse_instrument_configurations()
        )

        self._data_writer = DataWriter(
            *cfg_parser.parse_data_config(), self._instrument_rack.get_variable_names(units=True)
        )

        self._instrument_rack.instantiate_instruments()
        self._instrument_rack.initialise_settings()
        self._instrument_rack.configure_variables()

        self._thread = threading.Thread(target=self._main_loop, daemon=True)

        if running:
            self._data_writer.create_new_file()
            self._thread.start()

    @property
    def instrument_rack(self):
        return self._instrument_rack

    def stop(self):
        self._running = False

    def _main_loop(self):
        while self._running:
            self._instrument_rack.read_instruments()
            self._data_writer.write_data(self._instrument_rack.get_variable_values(units=True))
            time.sleep(self._update_time)
