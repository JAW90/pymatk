from dataclasses import dataclass
from .instrument_handling import _import_instrument


@dataclass
class InstrumentController:
    name: str
    module: str
    class_name: str
    input_: str
    output: str
    kwargs: dict | None = None

    def __post_init__(self):
        self._instance = _import_instrument(self.module, self.class_name, self.kwargs)

    # ARGH

    # This is a kind of interface? Or interpreter?
