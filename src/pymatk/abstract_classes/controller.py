from abc import abstractmethod
from typing import Any

from pymatk.abstract_classes import Subject, Observer


class Controller(Observer):
    @abstractmethod
    def update(self, subject: Subject) -> None:
        pass

    @property
    @abstractmethod
    def setpoint(self) -> Any:
        pass

    @setpoint.getter
    @abstractmethod
    def setpoint(self, setpoint: Any) -> None:
        pass
