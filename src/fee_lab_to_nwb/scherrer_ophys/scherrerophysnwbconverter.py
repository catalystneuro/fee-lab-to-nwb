"""Primary NWBConverter class for this dataset."""
from neuroconv import NWBConverter
from neuroconv.datainterfaces import VideoInterface

from fee_lab_to_nwb.scherrer_ophys.scherrerophysimaginginterface import (
    ScherrerOphysImagingInterface,
)
from fee_lab_to_nwb.scherrer_ophys.scherrerophyssegmentationinterface import (
    ScherrerOphysSegmentationInterface,
)


class ScherrerOphysNWBConverter(NWBConverter):
    """Primary conversion class for the optical imaging data of the Fee lab."""

    data_interface_classes = dict(
        Movie=VideoInterface,
        Ophys=ScherrerOphysImagingInterface,
        Segmentation=ScherrerOphysSegmentationInterface,
    )
