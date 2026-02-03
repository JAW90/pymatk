import pandas as pd

from dataclasses import dataclass


@dataclass
class DataFile:
    """
    Docstring for DataFile
    """

    filepath: str
    columns: list

    def __post_init__(self):
        """
        Docstring for __post_init__

        :param self: Description
        """
        self.header = ",".join(self.columns)
        with open(self.filepath, "w") as f:
            f.write(f"{self.header}\n")
        self.data: pd.DataFrame = pd.read_csv(self.filepath, header=0)
        self.current_data = pd.DataFrame(columns=self.columns, dtype=object)

    def append_to_csv(self, data):
        """
        Docstring for append_to_csv

        :param self: Description
        :param data: Description
        """
        self.current_data.loc[0] = data
        self.current_data.to_csv(
            self.filepath, mode="a", header=False, index=False
        )

    def get_all_data(self):
        """
        Docstring for get_all_data

        :param self: Description
        """
        return pd.read_csv(self.filepath, header=0)

    def get_last_line(self):
        """
        Docstring for get_last_line

        :param self: Description
        """
        df = pd.read_csv(self.filepath, chunksize=1000)

        last_row_df = None  # type: ignore

        for chunk in df:
            last_row_df: pd.DataFrame = chunk.tail()

        return dict(last_row_df.iloc[-1])
