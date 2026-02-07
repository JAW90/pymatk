import importlib
import sys

from pymatk.loaders.config_file_enums import InstrumentEnums


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


def _handle_get_function(
    instrument: object, get_func: str, return_element: int | str | None = None
):
    if not hasattr(instrument, get_func):
        raise AttributeError(
            f"Cannot find function/property '{get_func}' in instrument"
            + f" '{instrument}'. Check configuration."
        )
    # Easy to get reference to callable function of class/module
    if callable(getattr(instrument, get_func)):
        if return_element is not None:

            def element_of_function():
                return getattr(instrument, get_func)()[return_element]

            return element_of_function
        else:
            return getattr(instrument, get_func)
    # Need to wrap getting of non-callable attribute in a function
    # that can be called later
    else:
        if return_element is not None:

            def property_element_to_function():
                return getattr(instrument, get_func)[return_element]

            return property_element_to_function
        else:

            def property_to_function():
                return getattr(instrument, get_func)

            return property_to_function


def _handle_set_function(
    instrument,
    init_func: str,
    init_value: int | float | str | None = None,
    init_kwargs: dict | None = None,
):
    if not hasattr(instrument, init_func):
        raise AttributeError(
            f"Cannot find function/property '{init_func}' in instrument"
            + f" '{instrument}'. Check configuration."
        )
    # If it is not a function, try to set attribute to init_value
    if not callable(getattr(instrument, init_func)):
        if init_value is None:
            raise AttributeError(
                f"No '{InstrumentEnums.INIT_VALUE}' to pass to property '{init_func}'!"
                + " Check configuration."
            )
        else:
            try:
                setattr(
                    instrument,
                    init_func,
                    init_value,
                )
            except AttributeError:
                raise AttributeError(
                    f"Cannot initialise property '{instrument}:{init_func}'"
                    + f" with '{InstrumentEnums.INIT_VALUE}'={init_value}. Check configuration."
                )
    # Else it is callable. Try combination of init_value and init_kwargs
    else:
        try:
            if init_kwargs is None:
                if init_value is None:
                    getattr(instrument, init_func)

                else:
                    getattr(instrument, init_func)(init_value)

            elif init_kwargs:
                if not isinstance(init_kwargs, dict):
                    raise TypeError(f"{InstrumentEnums.KWARGS} must be of type dict.")
                if init_value is None:
                    getattr(instrument, init_func)(**init_kwargs)

                else:
                    getattr(instrument, init_func)(init_value, **init_kwargs)

        except AttributeError:
            raise AttributeError(
                f"Error when trying to initialise instrument {instrument}"
                + f" with {init_func}, {init_value}, {init_kwargs}. Check configuration."
            )
