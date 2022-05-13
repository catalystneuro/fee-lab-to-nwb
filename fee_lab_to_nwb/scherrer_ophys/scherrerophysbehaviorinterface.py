"""Primary class defining conversion of experiment-specific behavior."""
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

from pandas import read_csv, to_datetime

from nwb_conversion_tools.basedatainterface import BaseDataInterface
from pynwb import NWBFile

from ndx_events import Events


class ScherrerOphysBehaviorInterface(BaseDataInterface):
    """Data interface for adding the timestamps of behavioral data."""

    def __init__(
        self,
        behavior_data_file_path: str,
    ):
        super().__init__()
        self.behavior_data_file_path = Path(behavior_data_file_path)

        assert (
            self.behavior_data_file_path.suffix == ".csv"
        ), f"{behavior_data_file_path} should be a .csv"
        assert (
            self.behavior_data_file_path.exists()
        ), f"{behavior_data_file_path} does not exist"

        # first column is timestamps for frames in behavior video,
        # following the timestamp is additional tracking data, which can be ignored
        self.behavior_data = read_csv(
            self.behavior_data_file_path, sep=" ", header=None, usecols=[0]
        )

    def get_metadata(self):
        """Extracts metadata from the behavior data file name"""
        file_name = self.behavior_data_file_path.stem
        ind = [i for i, c in enumerate(file_name) if c.isdigit()][0]
        date_from_file_name = file_name[ind:]

        session_start_time = datetime.strptime(date_from_file_name, "%Y-%m-%dT%H_%M_%S")
        session_start_time = session_start_time.replace(tzinfo=ZoneInfo("US/Eastern"))

        metadata = dict(
            NWBFile=dict(
                session_start_time=str(session_start_time),
            )
        )

        return metadata

    def run_conversion(
        self, nwbfile: NWBFile, metadata: dict = None, overwrite: bool = False
    ):
        timestamp_in_datetime = to_datetime(self.behavior_data[0])
        elapsed_time_since_start = timestamp_in_datetime - timestamp_in_datetime.min()
        timestamps = elapsed_time_since_start.apply(
            lambda x: x.total_seconds()
        ).to_numpy()

        events = Events(
            name="BehaviorTimestamps",
            description="Timestamps for frames in behavior video "
            "as system time recorded by bonsai.",
            timestamps=timestamps,
        )

        behavior = nwbfile.create_processing_module(
            name="behavior", description="Processed behavioral data"
        )

        behavior.add(events)
