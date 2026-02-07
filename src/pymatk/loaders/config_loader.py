from pymatk.data_structures import VariablesCollection, DataConfig
from pymatk.loaders import (
    InstrumentEnums,
    VariableEnums,
    DataEnums,
    _handle_get_function,
    _handle_set_function,
    _import_instrument,
)

# TODO: Add docstrings


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
                    # dict.get returns None if not present
                    if VariableEnums.NAME in variable:
                        var_name = variable[VariableEnums.NAME]
                        return_element = variable.get(VariableEnums.RETURN_ELEMENT)
                        units = variable.get(VariableEnums.UNITS)
                        get_func = variable[VariableEnums.GET_FUNCTION]
                        method = _handle_get_function(instrument, get_func, return_element)
                        self._variables.add_variable(var_name, instrument_name, units, method)
                    else:
                        raise KeyError(
                            f"No valid variable {VariableEnums.NAME}!" + " Check configuration."
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
