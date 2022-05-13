"""Primary script to run to convert an entire session of data using the NWBConverter."""
from pathlib import Path

from nwb_conversion_tools.utils import load_dict_from_file, dict_deep_update
from fee_lab_to_nwb.scherrer_ophys import ScherrerOphysNWBConverter

ophys_dataset_path = Path("../../scherrer_ophys_data/")
ophys_dataset_session_id = ophys_dataset_path.stem
nwbfile_path = ophys_dataset_path / f"{ophys_dataset_session_id}.nwb"

metadata_path = Path(__file__).parent / "scherrer_ophys_metadata.yml"
metadata_from_yaml = load_dict_from_file(metadata_path)

source_data = dict(
    # Recording=dict(),
    # LFP=dict(),
    # Sorting=dict(),
    Behavior=dict(
        behavior_data_file_path=str(
            ophys_dataset_path / "home_pos-speed-in_2021-06-03T11_46_29.csv"
        )
    ),
)

ophys_dataset_converter = ScherrerOphysNWBConverter(source_data=source_data)

metadata = ophys_dataset_converter.get_metadata()
metadata = dict_deep_update(metadata, metadata_from_yaml)

ophys_dataset_converter.run_conversion(metadata=metadata, nwbfile_path=nwbfile_path)
