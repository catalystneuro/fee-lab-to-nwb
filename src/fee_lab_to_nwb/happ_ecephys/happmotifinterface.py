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
        motif_timestamps += imec_timestamps[indices] - audio_timestamps[indices]

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

        # Create the TimeIntervals for syllables
        for (syllable_name, (start_time, end_time)) in zip(
            syllable_names, zip(syllable_start_times, syllable_end_times)
        ):
            syllables.add_interval(
                label=syllable_name,
                start_time=start_time,
                stop_time=end_time,
            )

        return syllables

    def create_hierarchical_table_from_syllables(self, syllables: TimeIntervals):
        """Create a hierarchical table from the timings of motifs.
        The lowest hierarchical level is the level of syllables."""
        motifs_table = HierarchicalBehavioralTable(
            name="trials",
            description="The timings of motifs.",
            lower_tier_table=syllables,
        )

        syllable_names = self.motif_syllable_mapping["Syllable"].values
        for motif_ind, motif_name in enumerate(self.motifs[:, 0]):
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
        motif_timestamps = self.get_synchronized_motif_timestamps()

        # The TimeIntervals for syllables
        syllables = self.get_syllables_from_motif_timetamps(motif_timestamps=motif_timestamps)

        # Create a hierarchical table with syllables and motif timestamps
        motifs_table = self.create_hierarchical_table_from_syllables(
            syllables=syllables,
        )
        # Set the trials table to motifs
        nwbfile.trials = motifs_table
        # Add the syllables to the NWBFile
        nwbfile.add_time_intervals(syllables)
