"""Primary script to run to convert an entire session of data using the NWBConverter."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

from nwb_conversion_tools.utils import load_dict_from_file, dict_deep_update

from fee_lab_to_nwb.scherrer_ophys import (
    ScherrerOphysNWBConverter,
    ScherrerOphysImagingExtractor,
)
from utils import get_timestamps_from_csv

# The base folder path for ophys data
ophys_dataset_path = Path("../../scherrer_ophys_data/")
ophys_dataset_timestamp = "2021-06-03T11_46_29"
# The name of the NWB file
nwb_file_name = ophys_dataset_path.stem + "_" + ophys_dataset_timestamp


behavior_data_file_path = Path(f"./home_pos-speed-in_{ophys_dataset_timestamp}.csv")
behavior_movie_file_path = Path(f"./home_arena_{ophys_dataset_timestamp}.avi")
# Add a description for the behavior video
behavior_movie_description = "Behavior video of animal moving in environment at ~30 fps"

ophys_file_paths = [
    ophys_file_name
    for ophys_file_name in ophys_dataset_path.iterdir()
    if ophys_file_name.suffix == ".avi"
]
ophys_timestamp_file_path = ophys_dataset_path / f"invivo_{ophys_dataset_timestamp}.csv"

# The NWB file should be adjacent to the behavior movie file
nwbfile_path = behavior_movie_file_path.parent / f"{nwb_file_name}.nwb"

metadata_path = Path(__file__).parent / "scherrer_ophys_metadata.yml"
metadata_from_yaml = load_dict_from_file(metadata_path)

imaging_extractors = [
    ScherrerOphysImagingExtractor(file_path=file_path) for file_path in ophys_file_paths
]
ophys_timestamps = get_timestamps_from_csv(file_path=ophys_timestamp_file_path)
source_data = dict(
    Movie=dict(file_paths=[behavior_movie_file_path]),
    Ophys=dict(imaging_extractors=imaging_extractors, timestamps=ophys_timestamps),
)

timestamps = get_timestamps_from_csv(file_path=behavior_data_file_path)
conversion_options = dict(
    Movie=dict(external_mode=True, timestamps=timestamps),
)

ophys_dataset_converter = ScherrerOphysNWBConverter(source_data=source_data)

metadata = ophys_dataset_converter.get_metadata()
metadata = dict_deep_update(metadata, metadata_from_yaml)

session_start_time = datetime.strptime(ophys_dataset_timestamp, "%Y-%m-%dT%H_%M_%S")
session_start_time = session_start_time.replace(tzinfo=ZoneInfo("US/Eastern"))

metadata["NWBFile"].update(
    session_start_time=str(session_start_time),
    session_id=ophys_dataset_timestamp,
)

metadata["Behavior"]["Movies"][0].update(
    description=behavior_movie_description,
)

ophys_dataset_converter.run_conversion(
    metadata=metadata, nwbfile_path=nwbfile_path, conversion_options=conversion_options
)

# Make sure that the behavior movie file is in the same folder as the NWB file
assert all(
    file in list(behavior_movie_file_path.parent.iterdir())
    for file in [nwbfile_path, behavior_movie_file_path]
)
