from abc import ABC, abstractmethod
from typing import Any


class Variable(ABC):
    @abstractmethod
    def read(self) -> None:
        pass

    @property
    @abstractmethod
    def value(self) -> Any:
        pass
