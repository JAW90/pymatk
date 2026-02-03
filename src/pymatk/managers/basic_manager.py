import importlib
import sys
import tomllib

from enum import StrEnum

from pymatk.data_structures import (
    # DataFile,
    VariablesCollection,
)


class ConfigFileEnums(StrEnum):
    INSTRUMENTS = "instruments"
    MODULE = "module"
    CLASS = "class"
    KWARGS = "kwargs"
    VARIABLES = "variables"
    NAME = "name"
    UNITS = "units"
    GET_FUNCTION = "get_func"


class BasicManager:
    def __init__(self, name, config_file: str):
        self.name = name
        self._instruments = {}

        if not config_file.endswith(".toml"):
            raise ValueError("Not a valid .toml configuration files.")

        try:
            with open(config_file, "rb") as f:
                self._config = tomllib.load(f)
        except FileNotFoundError:
            print(f"Config file not found: {config_file}")

        # Read all the instruments and load modules
        self.load_instruments()
        # Setup variables collection
        self.initalise_variables()
        # TODO: Setup datafile

    def load_instruments(self):
        for instrument_name, config in self._config[
            ConfigFileEnums.INSTRUMENTS
        ].items():
            if config[ConfigFileEnums.MODULE] not in sys.modules:
                module = importlib.import_module(
                    config[ConfigFileEnums.MODULE]
                )
            else:
                module = sys.modules[config[ConfigFileEnums.MODULE]]

            if ConfigFileEnums.CLASS not in config:
                self._instruments[instrument_name] = module
            else:
                cls = getattr(module, config[ConfigFileEnums.CLASS])
                self._instruments[instrument_name] = cls(
                    **config[ConfigFileEnums.KWARGS]
                )

    def initalise_variables(self):
        self._variables = VariablesCollection(self.name)
        for instrument_name, variable in self._config[
            ConfigFileEnums.VARIABLES
        ].items():
            if instrument_name not in self._instruments:
                raise KeyError(
                    f"{instrument_name} not loaded yet in this collection."
                )
            else:
                instrument = self._instruments[instrument_name]

                for var_name, parameters in variable.items():
                    method = getattr(
                        instrument, parameters[ConfigFileEnums.GET_FUNCTION]
                    )
                    self._variables.add_variable(
                        parameters[ConfigFileEnums.NAME],
                        parameters[ConfigFileEnums.UNITS],
                        method,
                    )

    def update_variables(self):
        self._variables.update_variables()

    @property
    def all_values(self) -> dict:
        return self._variables.all_values
