import tomllib

# from pymatk.data_structures import (
#     # DataFile,
#     VariablesCollection,
# )
from pymatk.loaders import ConfigLoader


class BasicManager:
    def __init__(self, description, config_file: str):
        self.description = description
        self._instruments = {}

        if not config_file.endswith(".toml"):
            raise ValueError("Not a valid .toml configuration files.")

        try:
            with open(config_file, "rb") as f:
                self._config = tomllib.load(f)
        except FileNotFoundError:
            print(f"Config file not found: {config_file}")

        cfg_loader = ConfigLoader(self.description, self._config)

        self._instruments = cfg_loader.instruments
        self._variables = cfg_loader.variables

        # TODO: Setup datafile

    def update_variables(self):
        if self._variables is not None:
            self._variables.update_variables()

    @property
    def all_values(self) -> dict | None:
        if self._variables is not None:
            self.update_variables()
            return self._variables.all_values
        else:
            return None
