from typing import Optional

import numpy as np
from neuroconv.basedatainterface import BaseDataInterface
from pynwb import NWBFile
from scipy.io import loadmat


class MotifInterface(BaseDataInterface):
    """Data interface for adding timing of the motifs as trials to the NWB file."""

    def __init__(self, file_path: str, sync_file_path: str):
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

    def run_conversion(
        self,
        nwbfile: NWBFile,
        metadata: Optional[dict] = None,
    ):

        motif_timestamps = self.get_synchronized_motif_timestamps()
        motif_ids = self.motifs[:, 0]

        # Motif timestamps only denote the onset of the stimuli
        for (start_time, stop_time) in zip(motif_timestamps[::1], motif_timestamps[1::]):
            nwbfile.add_trial(start_time=start_time, stop_time=stop_time)
        # The last motif does not have a stop time
        nwbfile.add_trial(start_time=motif_timestamps[-1], stop_time=np.nan)

        nwbfile.add_trial_column(
            name="motif_id",
            description="Identifier of the repeating audio stimulus.",
            data=list(motif_ids),
        )
