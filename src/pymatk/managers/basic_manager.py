import threading
import time
import tomllib

from pymatk.data_structures import DataFile
from pymatk.loaders import ConfigLoader

# TODO: Logging / debugging


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

        cfg_loader = ConfigLoader(self.description, self._config)

        self._instruments = cfg_loader.instruments
        self._variables = cfg_loader.variables
        self._data_config = cfg_loader.data_config

        self._thread = threading.Thread(target=self._main_loop, daemon=True)

        if running:
            self.setup_new_datafile()
            self._thread.start()

    def setup_new_datafile(self):
        path, name = self._data_config.generate_new_file_path()
        filename = f"{path}/{name}.csv"
        columns = self._variables.variables_as_columns
        self._data_config.create_directory(path)
        self._datafile = DataFile(filename, columns)

    def _main_loop(self):
        if self._running:
            while True:
                self._variables.update_variables()
                self._datafile.append_to_csv(self._variables.latest_values)
                if self.debug:
                    print(self._variables.latest_values)
                time.sleep(self._update_time)
