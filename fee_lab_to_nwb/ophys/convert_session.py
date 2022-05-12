"""Primary script to run to convert an entire session of data using the NWBConverter."""
from pathlib import Path

from nwb_conversion_tools.utils import load_dict_from_file, dict_deep_update
from fee_lab_to_nwb.ophys import OphysDatasetNWBConverter

example_path = Path("D:/ExampleNWBConversion")
example_session_id = example_path.stem
nwbfile_path = example_path / f"{example_session_id}.nwb"

metadata_path = Path(__file__) / "fee_lab_metadata.yaml"
metadata_from_yaml = load_dict_from_file(metadata_path)

source_data = dict(
    Recording=dict(),
    LFP=dict(),
    Sorting=dict(),
    Behavior=dict(),
)

ophys_dataset_converter = OphysDatasetNWBConverter(source_data=source_data)

metadata = ophys_dataset_converter.get_metadata()
metadata = dict_deep_update(metadata, metadata_from_yaml)

ophys_dataset_converter.run_conversion(
    metadata=metadata, nwbfile_path=nwbfile_path
)
