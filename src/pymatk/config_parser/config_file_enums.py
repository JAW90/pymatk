from enum import StrEnum

# TODO: Add docstrings


class InstrumentConfigEnums(StrEnum):
    INSTRUMENTS = "instruments"
    MODULE = "module"
    CLASS = "class"
    KWARGS = "kwargs"
    INIT_SETTINGS = "initial_settings"
    SET_FUNC = "init_func"
    SET_VALUE = "init_value"
    VARIABLES = "variables"
    NAME = "name"
    UNITS = "units"
    GET_FUNC = "get_func"
    RETURN_ELEMENT = "return_element"


class DataConfigEnums(StrEnum):
    DATA = "data"
    PARENT_DIRECTORY = "parent_directory"
    FILESTEM = "filestem"
