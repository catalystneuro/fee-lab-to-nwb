"""Primary NWBConverter class for this dataset."""
from nwb_conversion_tools import (
    NWBConverter,
    SpikeGLXRecordingInterface,
    SpikeGLXLFPInterface,
    PhySortingInterface,
)

from fee_lab_to_nwb.ophysbehaviorinterface import OphysBehaviorInterface


class OphysDatasetNWBConverter(NWBConverter):
    """Primary conversion class for my extracellular electrophysiology dataset."""

    data_interface_classes = dict(
        #Recording=SpikeGLXRecordingInterface,
        #LFP=SpikeGLXLFPInterface,
        #Sorting=PhySortingInterface,
        Behavior=OphysBehaviorInterface,
    )
