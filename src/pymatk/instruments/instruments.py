from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List

from pymatk.abstract_classes import Observer, Subject
from pymatk.logging import logger
from .instrument_handling import _handle_get_function, _handle_set_function, _import_instrument


class Instrument(Subject):
    name: str
    module: str
    class_name: str | None = None
    kwargs: Dict[str, object] | None = None
    initial_settings: List["InstrumentSetting"] = field(default_factory=list)
    variables: Dict[str, InstrumentVariable] = field(default_factory=dict)

    def __init__(
        self,
        name: str,
        module: str,
        class_name: str | None = None,
        kwargs: Dict[str, object] | None = None,
        settings: Dict[str, InstrumentSetting] = {},
        variables: Dict[str, InstrumentVariable] = {},
    ):
        self.name = name
        self.module = module
        self.class_name = class_name
        self.kwargs = kwargs
        self.settings = settings
        self.variables = variables

        self._instantiated = False
        self._observers: List[Observer] = []

    def instantiate_instrument(self):
        if not self._instantiated:
            self._instance = _import_instrument(self.module, self.class_name, self.kwargs)
            self._instantiated = True

    def apply_initial_settings(self):
        if not self._instantiated:
            raise Exception(
                f"This instrument {self.name} has not been insantiated - cannot initialise."
            )
        else:
            for setting in self.settings.values():
                if setting.set_value is not None:
                    setting.apply_setting()

    def configure_variables(self):
        if not self._instantiated:
            raise Exception(
                f"This instrument {self.name} has not been instantiated"
                + " - cannot configure variables."
            )
        else:
            for variable in self.variables.values():
                variable.configure()
        self._configured = True

    def read(self):
        if not self._configured:
            raise Exception(f"Variables of '{self.name}' have not been configured.")
        else:
            for variable in self.variables.values():
                variable.read()
            self.notify()

    @property
    def instance(self):
        if self._instantiated:
            return self._instance

    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def notify(self):
        for observer in self._observers:
            observer.update(self)

    def get_variable_value(self, name):
        return self.variables[name].value

    def update_setting(
        self, setting_name: str, set_value: int | float | str | bool, set_kwargs=None
    ):
        setting = self.settings[setting_name]
        setting.set_value = set_value
        if set_kwargs:
            setting.set_kwargs = set_kwargs
        setting.apply_setting()


@dataclass
class InstrumentVariable:
    name: str
    units: str | None
    instrument: Instrument
    get_func: str
    return_element: int | str | None = None
    _value: int | float | str | bool | None = None
    _method: Callable | None = None

    def configure(self):
        self._method = _handle_get_function(
            self.instrument.instance, self.get_func, self.return_element
        )

    def read(self):
        if self._method is not None:
            self._value = self._method()
        else:
            raise Exception(f"Cannot call get method on variable {self.name}.")
        return self._value

    @property
    def value(self):
        return self._value


@dataclass
class InstrumentSetting:
    name: str
    instrument: Instrument
    set_func: str
    set_value: int | float | str | bool | None = None
    set_kwargs: Dict[str, object] | None = None

    def apply_setting(self):
        _handle_set_function(
            self.instrument.instance, self.set_func, self.set_value, self.set_kwargs
        )


class InstrumentRack:
    def __init__(self, name: str, instruments: Dict[str, Instrument] | None = None):
        self.name = name

        if instruments is not None and isinstance(instruments, dict):
            self._instruments = instruments
        elif not isinstance(instruments, dict):
            raise TypeError("Argument 'instruments' must either be None or Dict[str,Instrument].")
        else:
            self._instruments = {}

    def __repr__(self) -> str:
        response = f"{self.__class__.__name__}: '{self.name}'"
        for instrument_name, instrument in self._instruments.items():
            response += f"\n{instrument_name}: {instrument.module}.{instrument.class_name}"
        return response

    @property
    def instruments(self) -> Dict[str, Instrument]:
        return self._instruments

    def get_instrument(self, instrument_name: str):
        return self._instruments.get(instrument_name)

    def add_instrument(self, instrument: Instrument):
        if instrument.name in self._instruments:
            raise KeyError(
                f"Instrument with name {instrument.name} already added to"
                + f" {type(self).__name__} '{self.name}'."
            )
        else:
            self._instruments[instrument.name] = instrument

    def instantiate_instruments(self):
        [instrument.instantiate_instrument() for instrument in self._instruments.values()]
        logger.info("Instruments instantiated.")

    def apply_initial_settings(self):
        [instrument.apply_initial_settings() for instrument in self._instruments.values()]
        logger.info("Initial settings applied.")

    def configure_variables(self):
        [instrument.configure_variables() for instrument in self._instruments.values()]
        logger.info("Variables configured.")

    def get_variable_names(self, units=False) -> List[str]:
        all_variables = []
        for instrument in self._instruments.values():
            for variable in instrument.variables.values():
                if units and variable.units is not None:
                    var_string = f"{variable.name}({variable.units})"
                else:
                    var_string = f"{variable.name}"
                all_variables.append(var_string)
        return all_variables

    def read_instruments(self):
        [instrument.read() for instrument in self._instruments.values()]
        logger.debug("Read instruments:\n" + f"{self.get_variable_values(units=True)}")

    def get_variable_values(self, units=False) -> Dict[str, object]:
        all_values = {}
        for instrument in self._instruments.values():
            for variable in instrument.variables.values():
                if units and variable.units is not None:
                    name_format = f"{variable.name}({variable.units})"
                else:
                    name_format = f"{variable.name}"
                all_values[name_format] = variable.value
        return all_values
