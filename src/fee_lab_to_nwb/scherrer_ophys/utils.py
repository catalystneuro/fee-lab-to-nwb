"""Utility functions for this dataset."""
from pathlib import Path

import numpy as np
from neuroconv.utils import FilePathType
from pandas import read_csv, to_datetime, Series


def get_timestamps_from_csv(file_path: FilePathType) -> Series:
    """
    Extracts timestamps from a file.
    """

    if isinstance(file_path, str):
        file_path = Path(file_path)

    assert file_path.suffix == ".csv", f"{file_path} should be a .csv"
    assert file_path.exists(), f"{file_path} does not exist"

    data = read_csv(file_path, sep=" ", header=None, usecols=[0])

    timestamps = to_datetime(data[0])
    return timestamps


def shift_timestamps_to_start_from_zero(timestamps: Series) -> np.ndarray:
    """
    Returns the elapsed time in seconds since the first timestamp.
    """
    elapsed_time_since_start = timestamps - timestamps[0]
    return np.array(elapsed_time_since_start.apply(lambda x: x.total_seconds()))
