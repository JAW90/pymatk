from typing import Any

from pymatk.abstract_classes import Controller
from pymatk.instruments import Instrument, InstrumentRack  # noqa: F401


class TestController(Controller):
    def __init__(self, kwargs: dict[str, Any] | None = None):
        pass
        # self.state_kwargs = state_kwargs
        # self._running = running

        # if state_kwargs is not None and isinstance(state_kwargs, dict):
        #     self.configure_state()

    # def connect_to_rack(self, instrument_rack: InstrumentRack):
    #     self.instrument_rack = instrument_rack
    #     self._connected = True

    # def update(self, subject: Instrument) -> None:
    #     self.observed_value = subject.get_variable(self._observed_variable).value
    #     if self._running:
    #         self.update_output()

    # def update_output(self) -> None:
    #     if self._output_instrument is not None and self.observed_value is not None:
    #         self._output_instrument.update_setting(self._output_setting, self.observed_value)

    # def configure_input(self, instrument_name: str, variable_name: str) -> None:
    #     if self._connected:
    #         self._observed_instrument = self.instrument_rack.get_instrument(instrument_name)
    #         self._observed_variable = variable_name
    #         if self._observed_instrument is not None:
    #             self._observed_instrument.attach(self)
    #         else:
    #             raise KeyError(f"No instrument with name {instrument_name}!")
    #     else:
    #         raise Exception("Cannot configure. Controller must be connected to instrument rack.")

    # def configure_output(self, instrument_name: str, setting_name: str) -> None:
    #     if self._connected:
    #         self._output_instrument = self.instrument_rack.get_instrument(instrument_name)
    #         self._output_setting = setting_name
    #         if self._observed_instrument is None:
    #             raise KeyError(f"No instrument with name {instrument_name}!")
    #     else:
    #         raise Exception("Cannot configure. Controller must be connected to instrument rack.")

    # def configure_state(self) -> None:
    #     pass

    # def start(self) -> None:
    #     self._running = True

    # def stop(self) -> None:
    #     self._running = False
