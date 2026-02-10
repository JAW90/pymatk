import importlib
import sys

from pymatk.config_parser import InstrumentConfigEnums


def _import_instrument(module_name: str, class_name: str | None, instrument_kwargs: dict | None):
    if module_name not in sys.modules:
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            raise ImportError(
                f"Cannot import module '{module_name}'!"
                + " Check Python environment (module may not be installed) or"
                + " configuration file (misconfigured)."
            )
    else:
        module = sys.modules[module_name]

    if class_name is None:
        instrument = module
    else:
        try:
            cls = getattr(module, class_name)
        except AttributeError:
            raise AttributeError(
                f"Cannot find class {class_name} in module {module}!"
                + " Check configuration file for typos."
            )
        if instrument_kwargs is None:
            instrument = cls()
        else:
            instrument = cls(**instrument_kwargs)

    return instrument


def _handle_set_function(
    instrument_instance,
    set_func: str,
    set_value: int | float | str | None = None,
    set_kwargs: dict | None = None,
):
    if not hasattr(instrument_instance, set_func):
        raise AttributeError(
            f"Cannot find function/property '{set_func}' in instrument"
            + f" '{instrument_instance}'. Check configuration."
        )
    # If it is not a function, try to set attribute to set_value
    if not callable(getattr(instrument_instance, set_func)):
        if set_value is None:
            raise AttributeError(
                f"No '{InstrumentConfigEnums.SET_VALUE}' to pass to property '{set_func}'!"
                + " Check configuration."
            )
        else:
            try:
                setattr(
                    instrument_instance,
                    set_func,
                    set_value,
                )
            except AttributeError:
                raise AttributeError(
                    f"Cannot initialise property '{instrument_instance}:{set_func}'"
                    + f" with '{InstrumentConfigEnums.SET_VALUE}'={set_value}."
                    + " Check configuration."
                )
    # Else it is callable. Try combination of set_value and set_kwargs
    else:
        try:
            if set_kwargs is None:
                if set_value is None:
                    getattr(instrument_instance, set_func)

                else:
                    getattr(instrument_instance, set_func)(set_value)

            elif set_kwargs:
                if not isinstance(set_kwargs, dict):
                    raise TypeError(f"{InstrumentConfigEnums.KWARGS} must be of type dict.")
                if set_value is None:
                    getattr(instrument_instance, set_func)(**set_kwargs)

                else:
                    getattr(instrument_instance, set_func)(set_value, **set_kwargs)

        except AttributeError:
            raise AttributeError(
                f"Error when trying to initialise instrument {instrument_instance}"
                + f" with {set_func}, {set_value}, {set_kwargs}. Check configuration."
            )


def _handle_get_function(
    instrument_instance: object, get_func: str, return_element: int | str | None = None
):
    if not hasattr(instrument_instance, get_func):
        raise AttributeError(
            f"Cannot find function/property '{get_func}' in instrument"
            + f" '{instrument_instance}'. Check configuration."
        )
    # Easy to get reference to callable function of class/module
    if callable(getattr(instrument_instance, get_func)):
        if return_element is not None:

            def element_of_function():
                return getattr(instrument_instance, get_func)()[return_element]

            return element_of_function
        else:
            return getattr(instrument_instance, get_func)
    # Need to wrap getting of non-callable attribute in a function
    # that can be called later
    else:
        if return_element is not None:

            def property_element_to_function():
                return getattr(instrument_instance, get_func)[return_element]

            return property_element_to_function
        else:

            def property_to_function():
                return getattr(instrument_instance, get_func)

            return property_to_function
