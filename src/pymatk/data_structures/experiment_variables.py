from dataclasses import dataclass
from collections.abc import Callable
from typing import Dict

# TODO: Add docstrings

@dataclass
class ExperimentVariable:
    units: str | None
    get_func: Callable
    _value: object = None


class VariablesCollection:
    def __init__(self, name, variables: Dict[str, ExperimentVariable] | None = None):
        self.name = name

        if variables is not None:
            self._variables = variables
        else:
            self._variables = {}

    def __repr__(self) -> str:
        class_name = type(self).__name__
        repr_string = f"{class_name}: '{self.name}'\n Items:"
        for name, variable in self._variables.items():
            repr_string += f"\n{name}: {variable}"
        return repr_string

    # TODO: add __str__ function?

    def add_variable(self, name: str, units: str | None, get_function: Callable):
        if name in self._variables:
            raise KeyError(
                f"Variable with {name} already added to" + f" {type(self).__name__} '{self.name}'."
            )
        else:
            new_variable = ExperimentVariable(units, get_function)
            self._variables[name] = new_variable

    @property
    def variables_as_columns(self) -> list:
        columns = [f"{name}({variable.units})" for name, variable in self._variables.items()]
        return columns

    @property
    def all_variables(self) -> dict:
        return self._variables

    @property
    def latest_values(self) -> dict:
        variables_values = {
            f"{name}({variable.units})": variable._value
            for name, variable in self._variables.items()
        }
        return variables_values

    def update_variables(self):
        for var_name, variable in self._variables.items():
            variable._value = variable.get_func()
