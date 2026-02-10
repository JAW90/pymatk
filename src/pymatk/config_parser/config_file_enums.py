from enum import StrEnum

# TODO: Add docstrings


class InstrumentConfigEnums(StrEnum):
    INSTRUMENTS = "instruments"
    MODULE = "module"
    CLASS = "class"
    KWARGS = "kwargs"
    SETTINGS = "settings"
    SET_FUNC = "set_func"
    SET_VALUE = "set_value"
    VARIABLES = "variables"
    NAME = "name"
    UNITS = "units"
    GET_FUNC = "get_func"
    RETURN_ELEMENT = "return_element"


class DataConfigEnums(StrEnum):
    DATA = "data"
    PARENT_DIRECTORY = "parent_directory"
    FILESTEM = "filestem"


class ControllerConfigEnums(StrEnum):
    CONTROLLERS = "controllers"
    MODULE = "module"
    CLASS = "class"
    KWARGS = "kwargs"
