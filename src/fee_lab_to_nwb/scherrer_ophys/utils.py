"""Utility functions for this dataset."""
from pathlib import Path

from pandas import read_csv, to_datetime


def get_timestamps_from_csv(file_path: Path):
    """
    Extracts timestamps from a file.
    """

    assert file_path.suffix == ".csv", f"{file_path} should be a .csv"
    assert file_path.exists(), f"{file_path} does not exist"

    data = read_csv(file_path, sep=" ", header=None, usecols=[0])

    timestamp_in_datetime = to_datetime(data[0])
    elapsed_time_since_start = timestamp_in_datetime - timestamp_in_datetime.min()
    timestamps = elapsed_time_since_start.apply(lambda x: x.total_seconds()).to_list()

    return timestamps
