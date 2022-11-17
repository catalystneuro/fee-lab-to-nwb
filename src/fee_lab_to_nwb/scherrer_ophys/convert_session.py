"""Primary script to run to convert an entire session of data using the NWBConverter."""
from pathlib import Path
from zoneinfo import ZoneInfo

from natsort import natsorted
from neuroconv.utils import load_dict_from_file, dict_deep_update

from fee_lab_to_nwb.scherrer_ophys import ScherrerOphysNWBConverter
from utils import get_timestamps_from_csv, shift_timestamps_to_start_from_zero

# The base folder path for the calcium imaging data
ophys_folder_path = Path("/Volumes/t7-ssd/fee-lab-to-nwb/ophys")
# The timestamp for the recording
ophys_dataset_timestamp = "2021-07-26T13_50_50"

# The file path to the behavior movie file
behavior_movie_file_path = ophys_folder_path / f"home_arena_{ophys_dataset_timestamp}.avi"
# The timestamps for the behavior movie file
behavior_data_file_path = ophys_folder_path / f"home_pos-speed-in_{ophys_dataset_timestamp}.csv"
# Add a description for the behavior movie
behavior_movie_description = "Behavior video of animal moving in environment at ~30 fps"

# The list of file paths to the imaging (.avi) files
ophys_file_paths = [
    ophys_file_name
    for ophys_file_name in ophys_folder_path.iterdir()
    if ophys_file_name.suffix == ".avi" and ophys_file_name.stem.startswith("invivo")
]
# Sort the file paths to make sure they are in incremental order
ophys_file_paths = natsorted(ophys_file_paths)
# The timestamps for the imaging data
ophys_timestamp_file_path = ophys_folder_path / f"invivo_{ophys_dataset_timestamp}.csv"
# The file path to the extract output .mat file
segmentation_data_file_path = ophys_folder_path / "extract_output.mat"

# The NWB file path should be adjacent to the behavior movie file
nwbfile_path = behavior_movie_file_path.parent / f"{ophys_folder_path.stem}_{ophys_dataset_timestamp}.nwb"

metadata_path = Path(__file__).parent / "metadata.yml"
metadata_from_yaml = load_dict_from_file(metadata_path)

source_data = dict(
    Movie=dict(file_paths=[behavior_movie_file_path]),
    Ophys=dict(
        ophys_file_paths=ophys_file_paths,
        timestamps_file_path=str(ophys_timestamp_file_path),
    ),
    Segmentation=dict(
        file_path=str(segmentation_data_file_path),
        timestamps_file_path=str(ophys_timestamp_file_path),
    ),
)

ophys_times = get_timestamps_from_csv(file_path=ophys_timestamp_file_path)
behavior_times = get_timestamps_from_csv(file_path=behavior_data_file_path)
# The timings of optical imaging are missing timezone information, therefore
# we are adding the timezone information to the first time to get the offset
tzinfo = behavior_times[0].tz if behavior_times[0].tz is not None else ZoneInfo("US/Eastern")
offset = behavior_times[0] - ophys_times[0].replace(tzinfo=tzinfo)
offset_in_seconds = offset.total_seconds()
unadjusted_timestamps = shift_timestamps_to_start_from_zero(timestamps=behavior_times)
adjusted_timestamps = list(unadjusted_timestamps + offset_in_seconds)

conversion_options = dict(
    Movie=dict(external_mode=True, timestamps=adjusted_timestamps, starting_times=[adjusted_timestamps[0]]),
    Segmentation=dict(include_roi_acceptance=False),
)

ophys_dataset_converter = ScherrerOphysNWBConverter(source_data=source_data)

metadata = ophys_dataset_converter.get_metadata()
metadata = dict_deep_update(metadata, metadata_from_yaml)

# Use the first timestamp from the imaging recording as the start time of the session.
session_start_time = ophys_times[0].replace(tzinfo=tzinfo)

metadata["NWBFile"].update(
    session_start_time=session_start_time,
    session_id=ophys_dataset_timestamp,
)

metadata["Behavior"]["Movies"][0].update(
    description=behavior_movie_description,
)

ophys_dataset_converter.run_conversion(
    nwbfile_path=nwbfile_path, metadata=metadata, conversion_options=conversion_options
)

# Make sure that the behavior movie file is in the same folder as the NWB file
assert all(file in list(behavior_movie_file_path.parent.iterdir()) for file in [nwbfile_path, behavior_movie_file_path])
