import importlib
import sys

from pymatk.data_structures import VariablesCollection, DataConfig
from pymatk.loaders import InstrumentEnums, VariableEnums, DataEnums

# TODO: Add docstrings


def _import_instrument(module_name: str, class_name: str | None, instrument_kwargs: dict | None):
    if module_name not in sys.modules:
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            raise ImportError(
                f"Cannot import module '{module_name}'!"
                + " Check Python environment (module may not be installed) or"
                + " configuration file (misconfigured)."
            )
    else:
        module = sys.modules[module_name]

    if class_name is None:
        instrument = module
    else:
        try:
            cls = getattr(module, class_name)
        except AttributeError:
            raise AttributeError(
                f"Cannot find class {class_name} in module {module}!"
                + " Check configuration file for typos."
            )
        if instrument_kwargs is None:
            instrument = cls()
        else:
            instrument = cls(**instrument_kwargs)

    return instrument


def _handle_get_function(
    instrument: object, get_func: str, return_element: int | str | None = None
):
    if not hasattr(instrument, get_func):
        raise AttributeError(
            f"Cannot find function/property '{get_func}' in instrument"
            + f" '{instrument}'. Check configuration."
        )
    # Easy to get reference to callable function of class/module
    if callable(getattr(instrument, get_func)):
        if return_element is not None:

            def element_of_function():
                return getattr(instrument, get_func)()[return_element]

            return element_of_function
        else:
            return getattr(instrument, get_func)
    # Need to wrap getting of non-callable attribute in a function
    # that can be called later
    else:
        if return_element is not None:

            def property_element_to_function():
                return getattr(instrument, get_func)[return_element]

            return property_element_to_function
        else:

            def property_to_function():
                return getattr(instrument, get_func)

            return property_to_function


def _handle_set_function(
    instrument,
    init_func: str,
    init_value: int | float | str | None = None,
    init_kwargs: dict | None = None,
):
    if not hasattr(instrument, init_func):
        raise AttributeError(
            f"Cannot find function/property '{init_func}' in instrument"
            + f" '{instrument}'. Check configuration."
        )
    # If it is not a function, try to set attribute to init_value
    if not callable(getattr(instrument, init_func)):
        if init_value is None:
            raise AttributeError(
                f"No '{InstrumentEnums.INIT_VALUE}' to pass to property '{init_func}'!"
                + " Check configuration."
            )
        else:
            try:
                setattr(
                    instrument,
                    init_func,
                    init_value,
                )
            except AttributeError:
                raise AttributeError(
                    f"Cannot initialise property '{instrument}:{init_func}'"
                    + f" with '{InstrumentEnums.INIT_VALUE}'={init_value}. Check configuration."
                )
    # Else it is callable. Try combination of init_value and init_kwargs
    else:
        try:
            if init_kwargs is None:
                if init_value is None:
                    getattr(instrument, init_func)

                else:
                    getattr(instrument, init_func)(init_value)

            elif init_kwargs:
                if not isinstance(init_kwargs, dict):
                    raise TypeError(f"{InstrumentEnums.KWARGS} must be of type dict.")
                if init_value is None:
                    getattr(instrument, init_func)(**init_kwargs)

                else:
                    getattr(instrument, init_func)(init_value, **init_kwargs)

        except AttributeError:
            raise AttributeError(
                f"Error when trying to initialise instrument {instrument}"
                + f" with {init_func}, {init_value}, {init_kwargs}. Check configuration."
            )


class ConfigLoader:
    def __init__(self, description: str, config: dict):
        self.description = description
        self._config = config

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
        for instrument_name, instrument_config in self._config[
            InstrumentEnums.INSTRUMENTS
        ].items():
            module_name = instrument_config.get(InstrumentEnums.MODULE)
            class_name = instrument_config.get(InstrumentEnums.CLASS)
            instrument_kwargs = instrument_config.get(InstrumentEnums.KWARGS)

            self._instruments[instrument_name] = _import_instrument(
                module_name, class_name, instrument_kwargs
            )

            initialise_conditions = instrument_config.get(InstrumentEnums.INITIALISE)
            if initialise_conditions is not None:
                instrument = self._instruments[instrument_name]
                for condition in initialise_conditions:
                    init_func = condition.get(InstrumentEnums.INIT_FUNC)
                    if init_func is None:
                        raise AttributeError(
                            f"No function/property {InstrumentEnums.INIT_FUNC} provided to"
                            + " initialise! Check configuration."
                        )

                    init_func_kwargs = condition.get(InstrumentEnums.KWARGS)
                    init_value = condition.get(InstrumentEnums.INIT_VALUE)
                    _handle_set_function(instrument, init_func, init_value, init_func_kwargs)

    def initialise_variables(self):
        if self._instruments is None:
            raise AttributeError("No valid instruments.")

        self._variables = VariablesCollection(self.description)
        for instrument_name, variables in self._config[VariableEnums.VARIABLES].items():
            if instrument_name not in self._instruments:
                raise KeyError(
                    f"'{instrument_name}' not in this collection."
                    + " Check configuration file - is this instrument defined?"
                )
            else:
                instrument = self._instruments[instrument_name]
                for variable in variables:
                    print(variable)
                    print(type(variable))
                    # dict.get returns None if not present
                    if VariableEnums.NAME in variable:
                        var_name = variable[VariableEnums.NAME]
                        return_element = variable.get(VariableEnums.RETURN_ELEMENT)
                        units = variable.get(VariableEnums.UNITS)
                        get_func = variable[VariableEnums.GET_FUNCTION]
                        method = _handle_get_function(instrument, get_func, return_element)
                        self._variables.add_variable(var_name, units, method)
                    else:
                        raise KeyError(
                            f"No valid variable {VariableEnums.NAME}!" +
                            " Check configuration."
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
