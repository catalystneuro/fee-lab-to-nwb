"""Primary NWBConverter class for this dataset."""
from nwb_conversion_tools import (
    NWBConverter,
    SpikeGLXRecordingInterface,
    SpikeGLXLFPInterface,
    PhySortingInterface,
)

from fee_lab_to_nwb.scherrer_ophys import ScherrerOphysBehaviorInterface


class ScherrerOphysNWBConverter(NWBConverter):
    """Primary conversion class for my extracellular electrophysiology dataset."""

    data_interface_classes = dict(
        Behavior=ScherrerOphysBehaviorInterface,
    )
