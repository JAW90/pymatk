from dataclasses import dataclass
# from enum import IntEnum, auto


@dataclass
class Variable:
    name: str
    units: object
    method: object
    value: object = None


class VariablesCollection:
    pass


# class BackendVariables(IntEnum):
#     TIME = auto()
#     T_50K_STAGE = auto()
#     T_4K_PLATE = auto()
#     T_STATIC_VTI = auto()
#     T_DYNAMIC_VTI = auto()
#     T_50K_LINK = auto()
#     T_SAMPLE = auto()
#     NV_STATE = auto()
#     NV_SETPOINT = auto()
#     P_CIRC = auto()
#     NV_PID_STATE = auto()
#     HEAT_SWITCH_1_STATE = auto()
#     HEAT_SWITCH_2_STATE = auto()
#     HEATER_1_OUTPUT = auto()
#     HEATER_2_OUTPUT = auto()
