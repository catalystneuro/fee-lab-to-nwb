"""Primary NWBConverter class for this dataset."""
from neuroconv import (
    NWBConverter,
    SpikeGLXLFPInterface,
)


class HappEcephysNWBConverter(NWBConverter):
    """Primary conversion class for the SpikeGLX data of the Fee lab."""

    data_interface_classes = dict(
        SpikeGLXLFP=SpikeGLXLFPInterface,
    )

    def __init__(self, source_data):
        super().__init__(source_data)
