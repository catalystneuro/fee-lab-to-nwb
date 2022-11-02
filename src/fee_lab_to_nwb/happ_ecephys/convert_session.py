"""Primary script to run to convert an entire session of data using the NWBConverter."""
from pathlib import Path
from zoneinfo import ZoneInfo

from neuroconv.utils import dict_deep_update, load_dict_from_file

from fee_lab_to_nwb.happ_ecephys import HappEcephysNWBConverter
from fee_lab_to_nwb.happ_ecephys.utils import get_motif_syllables_table_for_session_date

# The base folder path for the SpikeGLX data
ecephys_dataset_path = Path("D:/Neuropixel")

# The name of the session
session_name = "7635_210729_LH_NCM"
subject_id, session_date, hemisphere, region = session_name.split("_")
hemisphere_readable = "left hemisphere" if "LH" in hemisphere else "right hemisphere"
experiment_folder = ecephys_dataset_path / f"{session_name}_g0"
# Provide a description for this session
session_description = (
    "Effect of habituation contra deviant stimuli over "
    f"the {hemisphere_readable} of Caudomedial Nidopallium ({region}) region."
)

# The filepath to the Neuropixels Dataset Log
ecephys_dataset_log_path = Path(__file__).parent / "Neuropixels_Dataset_Log.xlsx"
# The mapping between motifs and syllables
motif_syllables_table = get_motif_syllables_table_for_session_date(
    file_path=ecephys_dataset_log_path,
    session_date=session_date,
)
# Add a description for this experiment type
experiment_description = "no description"
if "Stim Notes" in motif_syllables_table:
    experiment_description = motif_syllables_table["Stim Notes"].drop_duplicates().values[0]

# The file path to the .ap.bin file
raw_file_path = experiment_folder / f"{session_name}_g0_imec0" / f"{session_name}_g0_t0.imec0.ap.bin"
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
    Motif=dict(
        file_path=str(motif_file_path),
        sync_file_path=str(sync_file_path),
        motif_syllable_mapping=motif_syllables_table.to_dict(),
    ),
    Audio=dict(file_path=str(audio_file_path)),
)

# The file path to the NWB file
nwbfile_path = f"{experiment_folder}/{session_name}.nwb"

# The metadata file path
metadata_path = Path(__file__).parent / "metadata.yml"
metadata_from_yaml = load_dict_from_file(metadata_path)

# The converter that combines the input streams into a single conversion
converter = HappEcephysNWBConverter(source_data=source_data)

# The converter can extract relevant metadata from the source files
metadata = converter.get_metadata()
# This metadata can be updated with other relevant metadata
metadata = dict_deep_update(metadata, metadata_from_yaml)

# Add subject_id to Subject metadata
metadata["Subject"].update(
    subject_id=subject_id,
)

# Add timezone information to session_start_time if missing
session_start_time = metadata["NWBFile"]["session_start_time"]
if not session_start_time.tzinfo:
    metadata["NWBFile"].update(
        session_start_time=session_start_time.replace(tzinfo=ZoneInfo("US/Eastern")),
    )
# Add metadata to NWBFile
metadata["NWBFile"].update(
    session_description=session_description,
    experiment_description=experiment_description,
)

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
    nwbfile_path=nwbfile_path,
    metadata=metadata,
    conversion_options=conversion_options,
)
