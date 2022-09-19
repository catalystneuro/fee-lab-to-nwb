"""Primary script to run to convert an entire session of data using the NWBConverter."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

from neuroconv.utils import load_dict_from_file, dict_deep_update

from fee_lab_to_nwb.scherrer_ophys import ScherrerOphysNWBConverter
from utils import get_timestamps_from_csv

# The base folder path for the calcium imaging data
ophys_folder_path = Path("../../scherrer_ophys_data/")
# The timestamp for the recording
ophys_dataset_timestamp = "2021-07-26T13_50_50"

# The file path to the behavior movie file
behavior_movie_file_path = ophys_folder_path / f"./home_arena_{ophys_dataset_timestamp}.avi"
# The timestamps for the behavior movie file
behavior_data_file_path = ophys_folder_path / f"home_pos-speed-in_{ophys_dataset_timestamp}.csv"
# Add a description for the behavior movie
behavior_movie_description = "Behavior video of animal moving in environment at ~30 fps"

# The list of file paths to the imaging (.avi) files
ophys_file_paths = [
    ophys_file_name for ophys_file_name in ophys_folder_path.iterdir() if ophys_file_name.suffix == ".avi"
]
# The timestamps for the imaging data
ophys_timestamp_file_path = ophys_folder_path / f"invivo_{ophys_dataset_timestamp}.csv"
# The file path to the extract output .mat file
segmentation_data_file_path = ophys_folder_path / "extract_output.mat"

metadata_path = Path(__file__).parent / "scherrer_ophys_metadata.yml"
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

# The NWB file path should be adjacent to the behavior movie file
nwbfile_path = behavior_movie_file_path.parent / f"stub_{ophys_folder_path.stem}_{ophys_dataset_timestamp}.nwb"

ophys_dataset_converter.run_conversion(
    nwbfile_path=nwbfile_path, metadata=metadata, conversion_options=conversion_options
)

# Make sure that the behavior movie file is in the same folder as the NWB file
assert all(file in list(behavior_movie_file_path.parent.iterdir()) for file in [nwbfile_path, behavior_movie_file_path])
