"""Primary NWBConverter class for this dataset."""
from neuroconv import NWBConverter
from neuroconv.datainterfaces import (
    SpikeGLXRecordingInterface,
    SpikeGLXLFPInterface,
    PhySortingInterface,
)


from fee_lab_to_nwb.happ_ecephys.happmotifinterface import MotifInterface

from fee_lab_to_nwb.general_interfaces import AudioInterface


class HappEcephysNWBConverter(NWBConverter):
    """Primary conversion class for the SpikeGLX data of the Fee lab."""

    data_interface_classes = dict(
        SpikeGLXRecording=SpikeGLXRecordingInterface,
        SpikeGLXLFP=SpikeGLXLFPInterface,
        Sorting=PhySortingInterface,
        Motif=MotifInterface,
        Audio=AudioInterface,
    )

    def __init__(self, source_data):
        super().__init__(source_data)
