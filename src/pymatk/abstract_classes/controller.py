from abc import abstractmethod

from pymatk.abstract_classes import Subject, Observer


class ControllerBase(Observer):
    @abstractmethod
    def update(self, subject: Subject) -> None:
        pass

    @abstractmethod
    def update_output(self) -> None:
        pass

    @abstractmethod
    def configure_input(self) -> None:
        pass

    @abstractmethod
    def configure_output(self) -> None:
        pass

    @abstractmethod
    def configure_state(self) -> None:
        pass

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass
