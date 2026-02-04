import importlib
import sys

from pymatk.data_structures import VariablesCollection
from pymatk.loaders import InstrumentEnums, VariableEnums


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


class ConfigLoader:
    def __init__(self, description: str, config: dict):
        self.description = description
        self._config = config
        self._instruments = {}
        self._variables = None
        self._outputs = {}

        # Load and configure instruments
        if InstrumentEnums.INSTRUMENTS in self._config:
            self.load_instruments()
        else:
            raise AttributeError("No instruments in config file. Check configuration.")

        if VariableEnums.VARIABLES in self._config:
            self.initalise_variables()

    def load_instruments(self):
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
                        f"Cannot find class {cls} in module {module}!" +
                        " Check configuration file for typos."
                    )
                if InstrumentEnums.KWARGS not in config:
                    self._instruments[instrument_name] = cls()
                else:
                    self._instruments[instrument_name] = cls(**config[InstrumentEnums.KWARGS])

    def initalise_variables(self):
        self._variables = VariablesCollection(self.description)
        for instrument_name, variable in self._config[VariableEnums.VARIABLES].items():
            if instrument_name not in self._instruments:
                raise KeyError(
                    f"'{instrument_name}' not in this collection." +
                    " Check configuration file - is this instrument defined?"
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
