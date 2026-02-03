from dataclasses import dataclass
from collections.abc import Callable
from typing import Dict
# from enum import IntEnum, auto


@dataclass
class ExperimentVariable:
    """
    Docstring for ExperimentVariable
    """

    name: str
    units: str | None
    get_func: Callable
    _value: object = None


class VariablesCollection:
    """
    Docstring for VariablesCollection
    """

    def __init__(
        self, name, variables: Dict[str, ExperimentVariable] | None = None
    ):
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
        for k, v in self._variables.items():
            repr_string += f"\n{k}: {v}"
        return repr_string

    # TODO: __str__ ?

    def add_variable(self, variable: ExperimentVariable):
        variable_name = variable.name

        if variable_name in self._variables:
            raise KeyError(
                f"{variable_name} already added to"
                + f" {type(self).__name__} '{self.name}'."
            )
        else:
            self._variables[variable_name] = variable

    @property
    def variable_columns(self) -> dict:
        """
        Docstring for variable_columns

        :param self: Description
        :return: Description
        :rtype: dict[Any, Any]
        """
        columns = {
            k: f"{v.name}({v.units})" for k, v in self._variables.items()
        }
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
        variables_values = {k: v._value for k, v in self._variables.items()}
        return variables_values
