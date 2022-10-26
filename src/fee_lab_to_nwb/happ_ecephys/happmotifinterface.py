from typing import Optional

import numpy as np
from ndx_hierarchical_behavioral_data import HierarchicalBehavioralTable
from neuroconv.basedatainterface import BaseDataInterface
from neuroconv.utils import ArrayType
from pynwb import NWBFile
from pynwb.epoch import TimeIntervals
from scipy.io import loadmat


class MotifInterface(BaseDataInterface):
    """Data interface for adding timing of the motifs as trials to the NWB file."""

    def __init__(self, file_path: str, sync_file_path: str, num_syllables_per_motif: int = 5):
        """
        Create the interface for writing the timing of the motifs to the NWB file.
        The motifs are added as trials.

        Parameters
        ----------
        file_path: str
            The path to the file containing the timing of the motifs.
        sync_file_path: str
            The path to the file containing the Audio and SpikeGLX timestamps for synchronization.
        """
        super().__init__(file_path=file_path)
        self.sync_file_path = sync_file_path
        self.motifs = self.read_motif_data()
        self.num_syllables_per_motif = num_syllables_per_motif

    def read_motif_data(self):
        """Reads the .mat file containing the timing of the motifs.
        Returns the identifier and timing of the motifs."""
        motif_data = loadmat(self.source_data["file_path"], squeeze_me=True, mat_dtype=True)
        assert "motifTimingData" in motif_data, "'motifTimingData' should be in file."

        motifs = motif_data["motifTimingData"]
        return motifs

    def get_synchronized_motif_timestamps(self):
        """Synchronizes the timings of motifs with the SpikeGLX timestamps."""
        motif_timestamps = self.motifs[:, 1]

        sync_data = loadmat(self.sync_file_path, squeeze_me=True, mat_dtype=True)
        assert "Audio_eventTimes" in sync_data, f"'Audio_eventTimes' should be in file."
        assert "IMEC_eventTimes" in sync_data, f"'IMEC_eventTimes' should be in file."

        audio_timestamps = sync_data["Audio_eventTimes"][0]
        imec_timestamps = sync_data["IMEC_eventTimes"][0]

        indices = np.searchsorted(audio_timestamps, motif_timestamps)
        motif_timestamps += (imec_timestamps[indices] - audio_timestamps[indices])

        return motif_timestamps

    def get_syllables_from_motif_timetamps(self, motif_timestamps: np.ndarray):
        """Returns the timings of syllables using the onset times of the motifs."""
        syllables = TimeIntervals(name="Syllables", description="The timings of syllables.")
        syllables.add_column("label", "The label of syllable.")
        syllable_start_times, syllable_end_times, syllable_names = [], [], []
        motif_syllable_mapping = self.motif_syllable_mapping
        for motif_name, motif_start_time in zip(self.motifs[:, 0], motif_timestamps):
            if len(self.motif_syllable_mapping["Song number"].value_counts()) > 1:
                motif_syllable_mapping = self.motif_syllable_mapping.loc[
                    self.motif_syllable_mapping["Motif name"] == motif_name
                ]
            # The first syllable onset in a motif is the same as the motif onset time
            syllable_start_time = motif_start_time
            for _, syllable in motif_syllable_mapping.iterrows():
                syllable_start_times.append(syllable_start_time)
                syllable_end_time = syllable_start_time + syllable["Length (seconds)"]
                syllable_end_times.append(syllable_end_time)
                syllable_names.append(syllable["Syllable"])
                syllable_start_time = syllable_end_time + syllable["Subsequent Silence (sec)"]

        return syllable_start_times, syllable_end_times, syllable_names

        for (syllable_label, (start_time, end_time)) in zip(
            syllables_labels, zip(syllables_start_times, syllables_end_times)
        ):
            syllables.add_interval(
                label=syllable_label,
                start_time=start_time,
                stop_time=end_time,
            )

        motifs_table = HierarchicalBehavioralTable(
            name="Motifs",
            description="The timings of motifs.",
            lower_tier_table=syllables,
        )
        motifs_table.add_column("motif_name", "The name of motif.")

        for motif_ind, motif_label in enumerate(self.motifs[:, 0]):
            motifs_table.add_interval(
                motif_name=motif_label.split("_")[1],
                label=motif_label,
                next_tier=np.arange(0, self.num_syllables_per_motif) + (self.num_syllables_per_motif * motif_ind),
            )

        return motifs_table

    def run_conversion(
        self,
        nwbfile: NWBFile,
        metadata: Optional[dict] = None,
    ):

        # Synchronize the timestamps of motifs with the SpikeGLX timestamps
        motif_timestamps = self.get_synchronized_motif_timestamps()

        # Get syllable timings
        syllable_start_times, syllable_end_times, syllable_names = self.get_syllables_from_motif_timetamps(
            motif_timestamps=motif_timestamps
        )

        # Add syllables as trials
        for start_time, stop_time in zip(syllable_start_times, syllable_end_times):
            nwbfile.add_trial(start_time=start_time, stop_time=stop_time)

        nwbfile.add_trial_column(
            name="syllable_name",
            description="Identifier of the syllable.",
            data=list(syllable_names),
        )

        # Create a hierarchical table with syllables and motif timestamps
        motifs_table = self.create_hierarchical_table_from_motif_timestamps(motif_timestamps=motif_timestamps)

        # Create behavioral processing module
        behavior_module = nwbfile.create_processing_module(
            name="behavior", description="The auditory stimulus of syllables and motifs."
        )
        # Add the hierarchical table to the processing module
        behavior_module.add(motifs_table)
