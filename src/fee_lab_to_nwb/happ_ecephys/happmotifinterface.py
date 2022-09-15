from typing import Optional

import numpy as np
from neuroconv.basedatainterface import BaseDataInterface
from pynwb import NWBFile
from scipy.io import loadmat


class MotifInterface(BaseDataInterface):
    """Data interface for adding timing of the motifs as trials to the NWB file."""

    def __init__(self, file_path: str):
        """
        Create the interface for writing the timing of the motifs to the NWB file.
        The motifs are added as trials.

        Parameters
        ----------
        file_path: str
            The path to the file containing the timing of the motifs.
        """
        super().__init__(file_path=file_path)

    def read_motif_data(self):
        """Reads the .mat file containing the timing of the motifs.
        Returns the identifier and timing of the motifs."""
        motif_data = loadmat(self.source_data["file_path"])
        assert "motifTimingData" in motif_data, "'motifTimingData' should be in file."

        motifs = motif_data["motifTimingData"]

        num_motifs = motifs.shape[0]
        motif_ids = [motifs[:, 0][motif_num][0] for motif_num in range(num_motifs)]
        motif_timestamp = [motifs[:, 1][motif_num][0][0] for motif_num in range(num_motifs)]
        return motif_ids, motif_timestamp

    def run_conversion(
        self,
        nwbfile: NWBFile,
        metadata: Optional[dict] = None,
    ):

        # todo: sync with session_start_time
        motif_ids, motif_timestamps = self.read_motif_data()

        start_times = motif_timestamps
        stop_times = motif_timestamps[1:]
        # the last timestamp does not have a stop time
        stop_times.append(np.nan)
        for (start_time, stop_time) in zip(start_times, stop_times):
            nwbfile.add_trial(start_time=start_time, stop_time=stop_time)

        nwbfile.add_trial_column(
            name="motif_id",
            description="Identifier of the repeating audio stimulus.",
            data=motif_ids,
        )
