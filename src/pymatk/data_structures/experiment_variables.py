from dataclasses import dataclass
from collections.abc import Callable
from typing import Dict


@dataclass
class ExperimentVariable:
    """
    Docstring for ExperimentVariable
    """

    units: str | None
    get_func: Callable
    _value: object = None


class VariablesCollection:
    """
    Docstring for VariablesCollection
    """

    def __init__(self, name, variables: Dict[str, ExperimentVariable] | None = None):
        """
        Docstring for __init__

        :param self: Description
        :param name: Description
        :param variables: Description
        :type variables: Dict[str, ExperimentVariable] | None
        """
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

    # TODO: __str__ ?

    def add_variable(self, name: str, units: str | None, get_function: Callable):
        if name in self._variables:
            raise KeyError(
                f"Variable with {name} already added to" + f" {type(self).__name__} '{self.name}'."
            )
        else:
            new_variable = ExperimentVariable(units, get_function)
            self._variables[name] = new_variable

    @property
    def variables_as_columns(self) -> dict:
        """
        Docstring for variables_as_columns

        :param self: Description
        :return: Description
        :rtype: dict[Any, Any]
        """
        columns = {name: f"{name}({variable.units})" for name, variable in self._variables.items()}
        return columns

    @property
    def all_variables(self) -> dict:
        """
        Docstring for all_variables

        :param self: Description
        :return: Description
        :rtype: dict[Any, Any]
        """
        return self._variables

    @property
    def all_values(self) -> dict:
        """
        Docstring for all_values

        :param self: Description
        :return: Description
        :rtype: dict[Any, Any]
        """
        variables_values = {name: variable._value for name, variable in self._variables.items()}
        return variables_values

    def update_variables(self):
        for var_name, variable in self._variables.items():
            variable._value = variable.get_func()
