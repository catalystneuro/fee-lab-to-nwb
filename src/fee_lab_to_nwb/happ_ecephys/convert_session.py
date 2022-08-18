"""Primary script to run to convert an entire session of data using the NWBConverter."""
from pathlib import Path

from neuroconv.utils import dict_deep_update, load_dict_from_file

from fee_lab_to_nwb.happ_ecephys import HappEcephysNWBConverter

# The base folder path for ecephys data
ecephys_dataset_path = Path("D:/Neuropixel")

# Point to the various files for the conversion
session_id = "9138"
session_date = "220228"  # YYMMDD
session_name = f"{session_id}_{session_date}_RH_NCM_g0"
experiment_folder = ecephys_dataset_path / session_name

# The name of the NWB file
nwbfile_path = str(Path(__file__).parent / f"{session_name}.nwb")

metadata_path = Path(__file__).parent / "happ_ecephys_metadata.yml"
metadata_from_yaml = load_dict_from_file(metadata_path)

raw_file_path = (
    experiment_folder / f"{session_name}_imec0" / f"{session_name}_t0.imec0.ap.bin"
)

lfp_file_path = raw_file_path.parent / raw_file_path.name.replace("ap", "lf")
# nidq_file_path = str(experiment_folder / f"{session_name}_t0.nidq.bin")

source_data = dict(
    SpikeGLXLFP=dict(file_path=str(lfp_file_path)),
)

ecephys_dataset_converter = HappEcephysNWBConverter(source_data=source_data)

metadata = ecephys_dataset_converter.get_metadata()
metadata = dict_deep_update(metadata, metadata_from_yaml)

conversion_options = dict(
    SpikeGLXLFP=dict(stub_test=True),
)

ecephys_dataset_converter.run_conversion(
    metadata=metadata, nwbfile_path=nwbfile_path, conversion_options=conversion_options
)
