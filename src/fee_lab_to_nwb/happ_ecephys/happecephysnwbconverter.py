"""Primary NWBConverter class for this dataset."""
from neuroconv import (
    NWBConverter,
    SpikeGLXRecordingInterface,
    SpikeGLXLFPInterface,
    PhySortingInterface,
)


class HappEcephysNWBConverter(NWBConverter):
    """Primary conversion class for the SpikeGLX data of the Fee lab."""

    data_interface_classes = dict(
        SpikeGLXRecording=SpikeGLXRecordingInterface,
        SpikeGLXLFP=SpikeGLXLFPInterface,
        Sorting=PhySortingInterface,
    )

    def __init__(self, source_data):
        super().__init__(source_data)
