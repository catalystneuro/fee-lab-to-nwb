from typing import Optional

import numpy as np
import pandas as pd

from ndx_hierarchical_behavioral_data import HierarchicalBehavioralTable
from neuroconv.basedatainterface import BaseDataInterface
from pynwb import NWBFile
from pynwb.epoch import TimeIntervals
from scipy.io import loadmat


class MotifInterface(BaseDataInterface):
    """Data interface for adding timing of the motifs as trials to the NWB file."""

    def __init__(
        self,
        file_path: str,
        sync_file_path: str,
        motif_syllable_mapping: dict,
    ):
        """
        Create the interface for writing the timing of the motifs to the NWB file.
        The motifs are added as trials.

        Parameters
        ----------
        file_path: str
            The path to the file containing the timing of the motifs.
        sync_file_path: str
            The path to the file containing the Audio and SpikeGLX timestamps for synchronization.
        motif_syllable_mapping: dict
            The dictionary that contains the duration of syllables and to which motif they belong.
        """
        super().__init__(file_path=file_path)
        self.sync_file_path = sync_file_path
        motifs = self.read_motif_timing_data()
        motif_struct_name = "motifTimingData"
        assert motif_struct_name in motifs, f"'{motif_struct_name}' should be in file."
        self.motif_names = motifs[motif_struct_name][:, 0]
        self.motif_timestamps = motifs[motif_struct_name][:, 1]
        # The syllables experiment has a separate column for syllables timings
        syllable_struct_name = "syll_phase_timingData"
        self.syllable_names = None
        self.syllable_timestamps = None
        if syllable_struct_name in motifs:
            self.syllable_names = motifs[syllable_struct_name][:, 0]
            self.syllable_timestamps = motifs[syllable_struct_name][:, 1]
        self.motif_syllable_mapping = pd.DataFrame.from_dict(motif_syllable_mapping)

    def read_motif_timing_data(self):
        """Reads the .mat file containing the timing of the motifs."""
        return loadmat(self.source_data["file_path"], squeeze_me=True, mat_dtype=True)

    def synchronize_timestamps(self, timestamps: np.ndarray) -> np.ndarray:
        """Synchronizes the timings of motifs with the SpikeGLX timestamps."""
        sync_data = loadmat(self.sync_file_path, squeeze_me=True, mat_dtype=True)
        assert "Audio_eventTimes" in sync_data, f"'Audio_eventTimes' should be in file."
        assert "IMEC_eventTimes" in sync_data, f"'IMEC_eventTimes' should be in file."

        audio_timestamps = sync_data["Audio_eventTimes"][0]
        imec_timestamps = sync_data["IMEC_eventTimes"][0]

        indices = np.searchsorted(audio_timestamps, timestamps)
        timestamps += imec_timestamps[indices] - audio_timestamps[indices]

        return timestamps

    def get_syllables_from_motif_timetamps(self, motif_timestamps: np.ndarray) -> TimeIntervals:
        """Returns the timings of syllables using the onset times of the motifs."""
        syllables_table = TimeIntervals(name="Syllables", description="The timings of syllables.")
        syllables_table.add_column("label", "The label of syllable.")
        syllable_start_times, syllable_end_times, syllable_names = [], [], []
        motif_syllable_mapping = self.motif_syllable_mapping
        for motif_name, motif_start_time in zip(self.motif_names, motif_timestamps):
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

        # Create the TimeIntervals for syllables
        for syllable_name, start_time, end_time in zip(syllable_names, syllable_start_times, syllable_end_times):
            syllables_table.add_interval(
                label=syllable_name,
                start_time=start_time,
                stop_time=end_time,
            )

        return syllables_table

    def create_hierarchical_table_from_syllables(self, syllables: TimeIntervals) -> HierarchicalBehavioralTable:
        """Create a hierarchical table from the timings of motifs.
        The lowest hierarchical level is the level of syllables."""
        motifs_table = HierarchicalBehavioralTable(
            name="trials",
            description="The timings of motifs.",
            lower_tier_table=syllables,
        )

        syllable_names = self.motif_syllable_mapping["Syllable"].values
        for motif_ind, motif_name in enumerate(self.motif_names):
            if len(self.motif_syllable_mapping["Song number"].value_counts()) > 1:
                motif_syllable_mapping = self.motif_syllable_mapping.loc[
                    self.motif_syllable_mapping["Motif name"] == motif_name
                ]
                syllable_names = motif_syllable_mapping["Syllable"].values

            start = len(syllable_names) * motif_ind
            stop = len(syllable_names) + start
            next_tier = list(np.arange(start=start, stop=stop))
            motifs_table.add_interval(
                label=motif_name,
                next_tier=next_tier,
            )

        return motifs_table

    def run_conversion(
        self,
        nwbfile: NWBFile,
        metadata: Optional[dict] = None,
    ):

        # Synchronize the timestamps of motifs with the SpikeGLX timestamps
        motif_timestamps = self.synchronize_timestamps(timestamps=self.motif_timestamps)

        # The TimeIntervals for syllables
        syllables_table = self.get_syllables_from_motif_timetamps(motif_timestamps=motif_timestamps)

        # Create a hierarchical table with syllables and motif timestamps
        motifs_table = self.create_hierarchical_table_from_syllables(
            syllables=syllables_table,
        )

        if self.syllable_timestamps is not None:
            syllable_timestamps = self.synchronize_timestamps(timestamps=self.syllable_timestamps)
            for syllable_name, syllable_start_time in zip(self.syllable_names, syllable_timestamps):
                # Look up silence duration after syllable onset in the mapping dict
                is_syllable_in_mapping = self.motif_syllable_mapping["Syllable"].isin(
                    [syllable_name, syllable_name[::-1]]
                )
                syllable_silence_duration = self.motif_syllable_mapping.loc[
                    is_syllable_in_mapping, "Subsequent Silence (sec)"
                ].values[0]
                # for missing syllable duration we assume duration of 0.02
                silence_duration = syllable_silence_duration or 0.02
                syllables_table.add_interval(
                    label=syllable_name,
                    start_time=syllable_start_time,
                    stop_time=syllable_start_time + silence_duration,
                )
        # Set the trials table to motifs
        nwbfile.trials = motifs_table
        # Add the syllables to the NWBFile
        nwbfile.add_time_intervals(syllables_table)
