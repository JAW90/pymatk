import importlib
import sys
import tomllib

from enum import StrEnum

from pymatk.data_structures import (
    # DataFile,
    VariablesCollection,
)


def _create_property_to_function(
    instrument: object, prop: str, return_element: int | str | None = None
):
    if return_element is not None:

        def property_element_to_function():
            return getattr(instrument, prop)[return_element]

        return property_element_to_function
    else:

        def property_to_function():
            return getattr(instrument, prop)

        return property_to_function


class ConfigFileEnums(StrEnum):
    INSTRUMENTS = "instruments"
    MODULE = "module"
    CLASS = "class"
    KWARGS = "kwargs"
    VARIABLES = "variables"
    NAME = "name"
    UNITS = "units"
    GET_FUNCTION = "get_func"
    PROPERTY = "property"
    RETURN_ELEMENT = "return_element"


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
                try:
                    module = importlib.import_module(
                        config[ConfigFileEnums.MODULE]
                    )
                except ImportError:
                    print(
                        f"Cannot import {config[ConfigFileEnums.MODULE]}!" +
                        " Check Python environment, or possible bad configuration."
                    )
            else:
                module = sys.modules[config[ConfigFileEnums.MODULE]]

            if ConfigFileEnums.CLASS not in config:
                self._instruments[instrument_name] = module
            else:
                cls = getattr(module, config[ConfigFileEnums.CLASS])
                if ConfigFileEnums.KWARGS not in config:
                    self._instruments[instrument_name] = cls()
                else:
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
                    return_element = parameters.get(
                        ConfigFileEnums.RETURN_ELEMENT
                    )  # Returns None if not present
                    if ConfigFileEnums.PROPERTY not in parameters:
                        method = getattr(
                            instrument,
                            parameters[ConfigFileEnums.GET_FUNCTION],
                            return_element,
                        )
                    elif parameters[ConfigFileEnums.PROPERTY]:
                        method = _create_property_to_function(
                            instrument,
                            parameters[ConfigFileEnums.GET_FUNCTION],
                            return_element,
                        )
                    else:
                        raise AttributeError(
                            "Bad Configuration {}".format(parameters)
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
        self.update_variables()
        return self._variables.all_values
