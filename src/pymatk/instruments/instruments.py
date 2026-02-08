from __future__ import annotations

import importlib
import sys

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from pymatk.config_parser import InstrumentConfigEnums
from pymatk.logging import logger


@dataclass
class Instrument:
    name: str
    module: str
    class_name: str | None = None
    kwargs: Dict[str, object] | None = None
    initial_settings: List[InstrumentSetting] = field(default_factory=list)
    variables: List[InstrumentVariable] = field(default_factory=list)
    _instance: object = None

    def instantiate_instrument(self):
        self._instance = self._import_instrument(self.module, self.class_name, self.kwargs)
        self._loaded = True

    def initialise_settings(self):
        if not self._loaded:
            raise Exception(
                f"This instrument {self.name} has not been loaded - cannot initialise."
            )
        else:
            for setting in self.initial_settings:
                self._handle_set_function(
                    self._instance, setting.set_func, setting.set_value, setting.set_kwargs
                )

    def configure_variables(self):
        if not self._loaded:
            raise Exception(
                f"This instrument {self.name} has not been loaded - cannot configure variables."
            )
        else:
            for variable in self.variables:
                variable._method = self._handle_get_function(
                    self._instance, variable.get_func, variable.return_element
                )
        self._configured = True

    def read(self):
        if not self._configured:
            raise Exception(f"This instrument '{self.name}' variables have not been configured.")
        else:
            for variable in self.variables:
                if variable._method is not None:
                    variable._value = variable._method()
                else:
                    raise Exception(f"Cannot call method on variable {variable}.")

    @staticmethod
    def _import_instrument(
        module_name: str, class_name: str | None, instrument_kwargs: dict | None
    ):
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

    @staticmethod
    def _handle_set_function(
        instrument_instance,
        set_func: str,
        set_value: int | float | str | None = None,
        set_kwargs: dict | None = None,
    ):
        if not hasattr(instrument_instance, set_func):
            raise AttributeError(
                f"Cannot find function/property '{set_func}' in instrument"
                + f" '{instrument_instance}'. Check configuration."
            )
        # If it is not a function, try to set attribute to set_value
        if not callable(getattr(instrument_instance, set_func)):
            if set_value is None:
                raise AttributeError(
                    f"No '{InstrumentConfigEnums.SET_VALUE}' to pass to property '{set_func}'!"
                    + " Check configuration."
                )
            else:
                try:
                    setattr(
                        instrument_instance,
                        set_func,
                        set_value,
                    )
                except AttributeError:
                    raise AttributeError(
                        f"Cannot initialise property '{instrument_instance}:{set_func}'"
                        + f" with '{InstrumentConfigEnums.SET_VALUE}'={set_value}."
                        + " Check configuration."
                    )
        # Else it is callable. Try combination of set_value and set_kwargs
        else:
            try:
                if set_kwargs is None:
                    if set_value is None:
                        getattr(instrument_instance, set_func)

                    else:
                        getattr(instrument_instance, set_func)(set_value)

                elif set_kwargs:
                    if not isinstance(set_kwargs, dict):
                        raise TypeError(f"{InstrumentConfigEnums.KWARGS} must be of type dict.")
                    if set_value is None:
                        getattr(instrument_instance, set_func)(**set_kwargs)

                    else:
                        getattr(instrument_instance, set_func)(set_value, **set_kwargs)

            except AttributeError:
                raise AttributeError(
                    f"Error when trying to initialise instrument {instrument_instance}"
                    + f" with {set_func}, {set_value}, {set_kwargs}. Check configuration."
                )

    @staticmethod
    def _handle_get_function(
        instrument_instance: object, get_func: str, return_element: int | str | None = None
    ):
        if not hasattr(instrument_instance, get_func):
            raise AttributeError(
                f"Cannot find function/property '{get_func}' in instrument"
                + f" '{instrument_instance}'. Check configuration."
            )
        # Easy to get reference to callable function of class/module
        if callable(getattr(instrument_instance, get_func)):
            if return_element is not None:

                def element_of_function():
                    return getattr(instrument_instance, get_func)()[return_element]

                return element_of_function
            else:
                return getattr(instrument_instance, get_func)
        # Need to wrap getting of non-callable attribute in a function
        # that can be called later
        else:
            if return_element is not None:

                def property_element_to_function():
                    return getattr(instrument_instance, get_func)[return_element]

                return property_element_to_function
            else:

                def property_to_function():
                    return getattr(instrument_instance, get_func)

                return property_to_function


@dataclass
class InstrumentVariable:
    name: str
    units: str | None
    instrument: Optional[Instrument]
    get_func: str
    return_element: int | str | None = None
    _value: object = None
    _method: Callable | None = None


@dataclass
class InstrumentSetting:
    instrument: Optional[Instrument]
    set_func: str
    set_value: int | float | str | None = None
    set_kwargs: Dict[str, object] | None = None


class InstrumentRack:
    def __init__(self, name: str, instruments: Dict[str, Instrument] | None = None):
        self.name = name

        if instruments is not None:
            self._instruments = instruments
        else:
            self._instruments = {}

    # TODO: __repr__
    def __repr__(self) -> str:
        response = f"{self.__class__.__name__}: '{self.name}'"
        for instrument_name, instrument in self._instruments.items():
            response += f"\n{instrument_name}: {instrument.module}.{instrument.class_name}"
        return response

    # @property
    # def instruments(self) -> Dict[str, Instrument]:
    #     return self._instruments

    # def add_instrument(self, instrument: Instrument):
    #     if instrument.name in self._instruments:
    #         raise KeyError(
    #             f"Instrument with {instrument.name} already added to"
    #             + f" {type(self).__name__} '{self.name}'."
    #         )
    #     else:
    #         self._instruments[instrument.name] = instrument

    def instantiate_instruments(self):
        [instrument.instantiate_instrument() for instrument in self._instruments.values()]
        logger.info("Instruments instantiated.")

    def initialise_settings(self):
        [instrument.initialise_settings() for instrument in self._instruments.values()]
        logger.info("Initial settings applied.")

    def configure_variables(self):
        [instrument.configure_variables() for instrument in self._instruments.values()]
        logger.info("Variables configured.")

    def get_variable_names(self, units=False) -> List[str]:
        all_variables = []
        for instrument in self._instruments.values():
            for variable in instrument.variables:
                if units and variable.units is not None:
                    var_string = f"{variable.name}({variable.units})"
                else:
                    var_string = f"{variable.name}"
                all_variables.append(var_string)
        return all_variables

    def read_instruments(self):
        [instrument.read() for instrument in self._instruments.values()]
        logger.debug(
            "Read instruments:\n"
            + f"{self.get_variable_values(units=True)}"
        )

    def get_variable_values(self, units=False) -> Dict[str, object]:
        all_values = {}
        for instrument in self._instruments.values():
            for variable in instrument.variables:
                if units and variable.units is not None:
                    name_format = f"{variable.name}({variable.units})"
                else:
                    name_format = f"{variable.name}"
                all_values[name_format] = variable._value
        return all_values

    # def add_variable_to_instrument(self, instrument_name: str, variable: InstrumentVariable):
    #     if instrument_name not in self._instruments:
    #         raise KeyError(
    #             f"No instrument with name '{instrument_name}' in this" +
    #             f"{type(self.__class__)}."
    #         )
    #     else:
    #         self._instruments[instrument_name].variables.append(variable)
