from typing import Dict, Tuple

from pymatk.instruments import Instrument, InstrumentSetting, InstrumentVariable
from pymatk.config_parser import InstrumentConfigEnums, DataConfigEnums, ControllerConfigEnums

# TODO: Add docstrings


class ConfigParser:
    def __init__(self, description: str, config: dict):
        self.description = description
        self._config = config

    def parse_data_config(self) -> Tuple[str, str]:
        parent_directory = self._config[DataConfigEnums.DATA].get(DataConfigEnums.PARENT_DIRECTORY)
        if parent_directory is None:
            raise AttributeError(f"No '{DataConfigEnums.PARENT_DIRECTORY}' specified.")
        filestem = self._config[DataConfigEnums.DATA].get(DataConfigEnums.FILESTEM)
        if filestem is None:
            raise AttributeError(f"No '{DataConfigEnums.FILESTEM}' specified.")
        return parent_directory, filestem

    def parse_instrument_configurations(self) -> Dict[str, Instrument]:
        self._instrument_configurations = {}
        for instrument_name, instrument_config in self._config[
            InstrumentConfigEnums.INSTRUMENTS
        ].items():
            module_name = instrument_config.get(InstrumentConfigEnums.MODULE)
            class_name = instrument_config.get(InstrumentConfigEnums.CLASS)
            instrument_kwargs = instrument_config.get(InstrumentConfigEnums.KWARGS)

            new_instrument = Instrument(
                instrument_name, module_name, class_name, instrument_kwargs
            )
            self._instrument_configurations[instrument_name] = new_instrument

            settings = self._config[instrument_name].get(InstrumentConfigEnums.SETTINGS)

            if settings is not None:
                for setting in settings:
                    set_name = setting.get(InstrumentConfigEnums.NAME)
                    if set_name is None:
                        raise KeyError(
                            f"No valid setting {InstrumentConfigEnums.NAME}!"
                            + " Check configuration."
                        )
                    set_func = setting.get(InstrumentConfigEnums.SET_FUNC)
                    set_kwargs = setting.get(InstrumentConfigEnums.KWARGS)
                    set_value = setting.get(InstrumentConfigEnums.SET_VALUE)
                    new_setting = InstrumentSetting(
                        set_name, new_instrument, set_func, set_value, set_kwargs
                    )
                    new_instrument.settings[set_name] = new_setting

            variables = self._config[instrument_name].get(InstrumentConfigEnums.VARIABLES)

            if variables is not None:
                for variable in variables:
                    variable_name = variable.get(InstrumentConfigEnums.NAME)
                    if variable_name is None:
                        raise KeyError(
                            f"No valid variable {InstrumentConfigEnums.NAME}!"
                            + " Check configuration."
                        )
                    units = variable.get(InstrumentConfigEnums.UNITS)
                    get_func = variable.get(InstrumentConfigEnums.GET_FUNC)
                    return_element = variable.get(InstrumentConfigEnums.RETURN_ELEMENT)
                    new_variable = InstrumentVariable(
                        variable_name, units, new_instrument, get_func, return_element
                    )
                    new_instrument.variables[variable_name] = new_variable

        return self._instrument_configurations

    def parse_controller_configuration(self):
        self._controller_configurations = {}
        for controller_name, controller_config in self._config[
            ControllerConfigEnums.CONTROLLERS
        ].items():
            module_name = controller_config.get(ControllerConfigEnums.MODULE)
            class_name = controller_config.get(ControllerConfigEnums.CLASS)
            controller_kwargs = controller_config.get(ControllerConfigEnums.KWARGS)
            print(controller_name, controller_config)
            # new_controller =
