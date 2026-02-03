import importlib
import sys
import tomllib

from pymatk.data_structures import (
    # DataFile,
    VariablesCollection,
)
from pathlib import Path


class BasicManager:
    def __init__(self, name, config_file: Path | str):
        self.name = name
        self._instruments = {}
        # TODO: check file exists
        # TODO: check is a TOML file
        # TODO: Read file into config dict

        # try:
        #     with open(config_file, 'rb') as f:
        #         self._config = tomllib.load(f)
        # except:
        #     print(f"Could not load config {config_file}!")
        #     ...

        with open(config_file, "rb") as f:
            self._config = tomllib.load(f)

        # Read all the instruments and load modules

        for instrument_name, config in self._config["instruments"].items():
            if "class" not in config:
                if config["module"] not in sys.modules:
                    module = importlib.import_module(config["module"])
                    self._instruments[instrument_name] = module
                else:
                    print(f"{config["module"]} in namespace")
                    self._instruments[instrument_name] = sys.modules[
                        config["module"]
                    ]
            else:
                if f"{config['module']}.{config['class']}" not in sys.modules:
                    module = importlib.import_module(config["module"])
                    cls = getattr(module, config["class"])
                    self._instruments[instrument_name] = cls(
                        **config["kwargs"]
                    )
                else:
                    self._instruments[instrument_name] = sys.modules[
                        f"{config['module']}.{config['class']}"
                    ]

        # Setup variables collection

        # self.initalise_variables()

    def initalise_variables(self):
        self._variables = VariablesCollection(self.name)
        for k, v in self._config["variables"].items():
            print(k, v)

    def update_variables(self):
        pass
