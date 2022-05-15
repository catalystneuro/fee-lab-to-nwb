"""Primary NWBConverter class for this dataset."""
from nwb_conversion_tools import (
    NWBConverter,
    SpikeGLXRecordingInterface,
    SpikeGLXLFPInterface,
    PhySortingInterface,
    MovieInterface,
)


class ScherrerOphysNWBConverter(NWBConverter):
    """Primary conversion class for my extracellular electrophysiology dataset."""

    data_interface_classes = dict(
        Movie=MovieInterface,
    )
