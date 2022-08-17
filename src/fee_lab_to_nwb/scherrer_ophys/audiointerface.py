from typing import Optional

from hdmf.backends.hdf5 import H5DataIO
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
        stub_test: bool = False,
        compression_options: Optional[dict] = None,
    ):

        audio_metadata = metadata["Behavior"]["Audio"][0]

        # TODO: this would be better to have its own function,
        # could also check whether this AcousticWaveformSeries with the name from metadata
        # already exists in the NWB file, and only add if it doesn't.

        # Load the audio file.
        file_path = self.source_data["file_path"]
        sampling_rate, data = wavfile.read(file_path, mmap=True)

        acoustic_waveform_series_kwargs = dict(
            rate=float(sampling_rate),
            starting_time=0.0,  # TODO: sync with recording start time
        )

        if stub_test:
            # Fast conversion for testing
            acoustic_waveform_series_kwargs.update(
                data=data[: (sampling_rate * 10)],
            )
        else:
            compression_options = compression_options or dict(compression="gzip")
            acoustic_waveform_series_kwargs.update(
                data=H5DataIO(data, **compression_options),
            )

        # Add metadata
        acoustic_waveform_series_kwargs.update(**audio_metadata)

        # Create AcousticWaveformSeries with ndx-sound
        acoustic_waveform_series = AcousticWaveformSeries(
            **acoustic_waveform_series_kwargs
        )

        # Add audio recording to nwbfile as acquisition
        # TODO: double check if this is indeed acquired and not stimuli
        nwbfile.add_acquisition(acoustic_waveform_series)
