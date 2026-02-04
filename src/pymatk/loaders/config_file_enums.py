from enum import StrEnum


class InstrumentEnums(StrEnum):
    INSTRUMENTS = "instruments"
    MODULE = "module"
    CLASS = "class"
    KWARGS = "kwargs"


class VariableEnums(StrEnum):
    VARIABLES = "variables"
    UNITS = "units"
    GET_FUNCTION = "get_func"
    PROPERTY = "is_property"
    RETURN_ELEMENT = "return_element"


class DataEnums(StrEnum):
    DATA = "data"
    OUTPUT_DIRECTORY = "output_directory"
    FILESTEM = "filestem"
