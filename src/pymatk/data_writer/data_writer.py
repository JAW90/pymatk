import datetime
import os
import pandas as pd

from dataclasses import dataclass
from typing import Tuple

# TODO: Add docstrings


@dataclass
class DataWriter:
    parent_directory: str
    filestem: str
    columns: list

    def create_new_file(self):
        self.header = ",".join(self.columns)
        self.filename,  self.out_directory = self.get_new_file_and_path()
        self.full_file_path = f"{self.out_directory}/{self.filename}"
        self.create_directory(self.out_directory)
        with open(self.full_file_path, "w") as f:
            f.write(f"{self.header}\n")
        self.temp_data: pd.DataFrame = pd.read_csv(self.full_file_path, header=0)

    def get_new_file_and_path(self) -> Tuple[str, str]:
        now = datetime.datetime.now()
        ymd_hms = now.strftime("%y%m%d_%H%M%S")
        ymd = now.strftime("%y%m%d")
        return (
            f"{self.filestem}_{ymd_hms}.csv",
            f"{self.parent_directory}/{self.filestem}/{ymd}",
        )

    @staticmethod
    def create_directory(path):
        if not os.path.isdir(path):
            os.makedirs(path)

    def write_data(self, data):
        self.temp_data.loc[0] = data
        self.temp_data.to_csv(self.full_file_path, mode="a", header=False, index=False)
