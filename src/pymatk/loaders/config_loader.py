import importlib
import sys

from pymatk.data_structures import VariablesCollection, DataConfig
from pymatk.loaders import InstrumentEnums, VariableEnums, DataEnums

# TODO: Add docstrings


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


# TODO: Implement instruments initialisation


class ConfigLoader:
    def __init__(self, description: str, config: dict):
        self.description = description
        self._config = config
        # self._data_config = None
        # self._instruments = None
        # self._variables = None
        # self._outputs = None

        if DataEnums.DATA in self._config:
            self.load_data_config()
        else:
            raise AttributeError("No data configuration in config file. Check configuratoin.")

        if InstrumentEnums.INSTRUMENTS in self._config:
            self.load_instruments()
        else:
            raise AttributeError("No instruments in config file. Check configuration.")

        if VariableEnums.VARIABLES in self._config:
            self.initialise_variables()
        else:
            raise AttributeError("No variables in config file. Check configuration.")

    def load_data_config(self):
        output_directory = self._config[DataEnums.DATA].get(DataEnums.OUTPUT_DIRECTORY)
        if output_directory is None:
            raise AttributeError(f"No '{DataEnums.OUTPUT_DIRECTORY}' specified.")
        filestem = self._config[DataEnums.DATA].get(DataEnums.FILESTEM)
        if filestem is None:
            raise AttributeError(f"No '{DataEnums.FILESTEM}' specified.")
        self._data_config = DataConfig(output_directory, filestem)

    def load_instruments(self):
        self._instruments = {}
        for instrument_name, config in self._config[InstrumentEnums.INSTRUMENTS].items():
            if config[InstrumentEnums.MODULE] not in sys.modules:
                try:
                    module = importlib.import_module(config[InstrumentEnums.MODULE])
                except ImportError:
                    raise ImportError(
                        f"Cannot import module '{config[InstrumentEnums.MODULE]}'!"
                        + " Check Python environment (module may not be installed) or"
                        + " configuration file (misconfigured)."
                    )
            else:
                module = sys.modules[config[InstrumentEnums.MODULE]]

            if InstrumentEnums.CLASS not in config:
                self._instruments[instrument_name] = module
            else:
                try:
                    cls = getattr(module, config[InstrumentEnums.CLASS])
                except AttributeError:
                    raise AttributeError(
                        f"Cannot find class {cls} in module {module}!"
                        + " Check configuration file for typos."
                    )
                if InstrumentEnums.KWARGS not in config:
                    self._instruments[instrument_name] = cls()
                else:
                    self._instruments[instrument_name] = cls(**config[InstrumentEnums.KWARGS])

    def initialise_variables(self):
        if self._instruments is None:
            raise AttributeError("No valid instruments.")

        self._variables = VariablesCollection(self.description)
        for instrument_name, variable in self._config[VariableEnums.VARIABLES].items():
            if instrument_name not in self._instruments:
                raise KeyError(
                    f"'{instrument_name}' not in this collection."
                    + " Check configuration file - is this instrument defined?"
                )
            else:
                instrument = self._instruments[instrument_name]
                for var_name, parameters in variable.items():
                    return_element = parameters.get(
                        VariableEnums.RETURN_ELEMENT
                    )  # Returns None if not present
                    if VariableEnums.PROPERTY not in parameters:
                        method = getattr(
                            instrument,
                            parameters[VariableEnums.GET_FUNCTION],
                            return_element,
                        )
                    elif parameters[VariableEnums.PROPERTY]:
                        method = _create_property_to_function(
                            instrument,
                            parameters[VariableEnums.GET_FUNCTION],
                            return_element,
                        )
                    else:
                        raise AttributeError("Bad Configuration {}".format(parameters))
                    self._variables.add_variable(
                        var_name,
                        parameters[VariableEnums.UNITS],
                        method,
                    )

    @property
    def instruments(self):
        return self._instruments

    @property
    def variables(self):
        return self._variables

    @property
    def config(self):
        return self._config

    @property
    def data_config(self):
        return self._data_config
