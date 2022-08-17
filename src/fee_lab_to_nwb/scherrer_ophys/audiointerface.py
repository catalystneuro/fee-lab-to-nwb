from typing import Optional

from neuroconv.basedatainterface import BaseDataInterface
from neuroconv.utils import get_schema_from_hdmf_class, get_base_schema
from pynwb import NWBFile, TimeSeries
from scipy.io import wavfile

from ndx_sound import AcousticWaveformSeries


class AudioInterface(BaseDataInterface):
    """Data interface for writing acoustic recording to an NWB file."""

    def __init__(self, file_path: str):
        """
        Create the interface for writing acoustic recording to an NWB file.

        Parameters
        ----------
        file_path: str
            The path to the audio file.
        """
        super().__init__(file_path=file_path)

    def get_metadata_schema(self):
        metadata_schema = super().get_metadata_schema()
        time_series_metadata_schema = get_schema_from_hdmf_class(TimeSeries)
        exclude = ["conversion", "starting_time", "rate"]
        for key in exclude:
            time_series_metadata_schema["properties"].pop(key)
        metadata_schema["properties"]["Behavior"] = get_base_schema(tag="Behavior")
        metadata_schema["properties"]["Behavior"].update(
            required=["Audio"],
            properties=dict(
                Audio=dict(
                    type="array",
                    minItems=1,
                    items=time_series_metadata_schema,
                )
            ),
        )
        return metadata_schema

    def run_conversion(
        self,
        nwbfile: Optional[NWBFile] = None,
        metadata: Optional[dict] = None,
    ):

        audio_metadata = metadata["Behavior"]["Audio"][0]

        # Load the audio file.
        file_path = self.source_data["file_path"]
        sampling_rate, samples = wavfile.read(file_path, mmap=True)

        # create AcousticWaveformSeries with ndx-sound
        acoustic_waveform_series = AcousticWaveformSeries(
            name=audio_metadata["name"],
            data=samples,  # TODO: wrap into H5DataIO?
            rate=float(sampling_rate),
            description=audio_metadata["description"],
            starting_time=0.0,  # TODO: sync with recording start time
        )

        # add audio recording to nwbfile as acquisition
        nwbfile.add_acquisition(acoustic_waveform_series)
