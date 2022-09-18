"""Primary script to run to convert an entire session of data using the NWBConverter."""
from pathlib import Path

from neuroconv.utils import dict_deep_update, load_dict_from_file

from fee_lab_to_nwb.happ_ecephys import HappEcephysNWBConverter

# The base folder path for the SpikeGLX data
ecephys_dataset_path = Path("D:/Neuropixel")

# Point to the various files for the conversion
session_id = "7635"  # "9060"
session_date = "210729"  # YYMMDD
session_name = f"{session_id}_{session_date}_LH_NCM_g0"
experiment_folder = ecephys_dataset_path / session_name

# The file path to the .ap.bin file
raw_file_path = experiment_folder / f"{session_name}_imec0" / f"{session_name}_t0.imec0.ap.bin"
# The file path to the .lf.bin file
lfp_file_path = raw_file_path.parent / raw_file_path.name.replace("ap", "lf")
# The folder path to Phy sorting output
phy_folder_path = raw_file_path.parent
# The file path to the Audio file
audio_file_path = experiment_folder / f"micData_{session_date}.wav"
# The file path to timing of motifs
motif_file_path = experiment_folder / f"timingData_{session_date}.mat"
# The file path to synchronize the timing of motifs
sync_file_path = experiment_folder / f"syncData_{session_date}.mat"

# The input streams that point to various files
source_data = dict(
    SpikeGLXRecording=dict(file_path=str(raw_file_path)),
    SpikeGLXLFP=dict(file_path=str(lfp_file_path)),
    Sorting=dict(folder_path=str(raw_file_path.parent)),
    Motif=dict(file_path=str(motif_file_path), sync_file_path=str(sync_file_path)),
    Audio=dict(file_path=str(audio_file_path)),
)

# The file path to the NWB file
nwbfile_path = f"/Volumes/t7-ssd/7635_210729_LH_NCM_g0/{session_name}.nwb"

# The metadata file path
metadata_path = "happ_ecephys_metadata.yml"
metadata_from_yaml = load_dict_from_file(metadata_path)

# The converter that combines the input streams into a single conversion
converter = HappEcephysNWBConverter(source_data=source_data)

# The converter can extract relevant metadata from the source files
metadata = converter.get_metadata()
# This metadata can be updated with other relevant metadata
metadata = dict_deep_update(metadata, metadata_from_yaml)

# For fast conversion enable stub_test
# To convert the entire session use iterator_type="v2" for the SpikeGLX data
conversion_options = dict(
    SpikeGLXRecording=dict(
        stub_test=True,
    ),
    SpikeGLXLFP=dict(
        stub_test=True,
    ),
)

# Run the conversion
converter.run_conversion(
    metadata=metadata,
    nwbfile_path=nwbfile_path,
    conversion_options=conversion_options,
)
