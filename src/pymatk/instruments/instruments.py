from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

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

        self._observers: List[Observer] = []

        self._instance = _import_instrument(self.module, self.class_name, self.kwargs)

        for setting in self.settings.values():
            if setting.set_value is not None:
                setting.apply_setting()

    def read(self):
        for variable in self.variables.values():
            variable.read()
        self.notify()

    @property
    def instance(self):
        return self._instance

    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def notify(self) -> None:
        for observer in self._observers:
            observer.update(self)

    def get_variable(self, name: str) -> InstrumentVariable:
        return self.variables[name]

    def update_setting(
        self, setting_name: str, set_value: int | float | str | bool, set_kwargs=None
    ):
        setting = self.settings[setting_name]
        setting.set_value = set_value
        if set_kwargs:
            setting.set_kwargs = set_kwargs
        setting.apply_setting()


class InstrumentVariable(Subject):
    def __init__(
        self,
        name: str,
        units: str | None,
        parent_instrument: Instrument,
        get_func: str,
        return_element: int | str | None = None,
    ):
        self.name = name
        self.units = units
        self.parent_instrument = parent_instrument
        self.get_func = get_func
        self.return_element = return_element

        self._value = None
        self._method = None

        self._observers: List[Observer] = []

        self._method = _handle_get_function(
            self.parent_instrument.instance, self.get_func, self.return_element
        )

    def read(self):
        if self._method is not None:
            self._value = self._method()
        else:
            raise Exception(f"Cannot call get method on variable {self.name}.")
        self.notify()
        return self._value

    @property
    def value(self):
        return self._value

    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def notify(self):
        for observer in self._observers:
            observer.update(self)


# TODO: Implement ControllerVariable


class ControllerVariable(InstrumentVariable):
    def __init__(self):
        pass


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


class InstrumentRack(Subject):
    def __init__(self, name: str, instruments: Dict[str, Instrument] | None = None):
        self.name = name

        if instruments is not None and isinstance(instruments, dict):
            self._instruments = instruments
        elif not isinstance(instruments, dict):
            raise TypeError("Argument 'instruments' must either be None or Dict[str,Instrument].")
        else:
            self._instruments = {}

        self._observers = []

        self._controllers = {}

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
        logger.debug("Read instruments:\n" + f"{self.readings}")
        # Read controller variables
        # Store last set of readings in memory
        # Notify observers, e.g. DataWriter
        self.notify()

    @property
    def readings(self) -> Dict[str, object] | None:
        readings = {}
        for instrument in [*self._instruments.values(), *self._controllers.values()]:
            for variable in instrument.variables.values():
                if variable.units is not None:
                    name_format = f"{variable.name}({variable.units})"
                else:
                    name_format = f"{variable.name}"
                readings[name_format] = variable.value

        return readings

    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def notify(self):
        for observer in self._observers:
            observer.update(self)
