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

        first_timestamp_difference = imec_timestamps[0] - audio_timestamps[0]
        audio_timestamps += first_timestamp_difference

        all_timestamp_difference = imec_timestamps - audio_timestamps
        xsorted = np.argsort(audio_timestamps)
        ypos = np.searchsorted(audio_timestamps[xsorted], motif_timestamps)
        indices = xsorted[ypos]

        motif_timestamps += all_timestamp_difference[indices]

        return motif_timestamps

    def create_hierarchical_table_from_motif_timestamps(self, motif_timestamps: ArrayType):
        """Create a hierarchical table from the timings of motifs.
        The lowest hierarchical level is the level of syllables. The number of
        syllables within a motif is assumed to be fixed per experiment. The latency
        of each syllable is fixed for now, but should be modified in the future given
        more information about the mapping between motifs and syllables."""
        syllables = TimeIntervals(name="Syllables", description="desc")
        syllables.add_column("label", "The label of syllable.")

        syllables_start_times, syllables_end_times = [], []
        motif_start_times = list(motif_timestamps[::1])
        motif_end_times = list(motif_timestamps[1::])
        motif_end_times.append(np.nan)  # the last num_syllables_per_motif will be nan
        for (start_time, end_time) in zip(motif_start_times, motif_end_times):
            # Construct the timings of syllables from motif timestamps,
            # assuming that the number of syllables within motifs are ALWAYS the same.
            syllable_onset_times = np.linspace(
                start=start_time,
                stop=end_time,
                num=self.num_syllables_per_motif,
                endpoint=False,
            )
            syllables_start_times.extend(syllable_onset_times)
            # Until we can reverse-engineer the latency of each syllable from the mapping
            syllables_latency = np.nanmedian(np.diff(syllable_onset_times))
            syllables_end_times.extend(syllable_onset_times + syllables_latency)

        # Until we lack the mapping between motifs and syllables we assume these labels
        syllables_labels = ["a", "b", "c", "d", "e"] * len(motif_timestamps)

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
        # Create a hierarchical table with syllables and motif timestamps
        motifs_table = self.create_hierarchical_table_from_motif_timestamps(motif_timestamps=motif_timestamps)

        # Create behavioral processing module
        behavior_module = nwbfile.create_processing_module(
            name="behavior", description="The auditory stimulus of syllables and motifs."
        )
        # Add the hierarchical table to the processing module
        behavior_module.add(motifs_table)
