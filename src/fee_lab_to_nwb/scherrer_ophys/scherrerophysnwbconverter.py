"""Primary NWBConverter class for this dataset."""
from nwb_conversion_tools import (
    NWBConverter,
    MovieInterface,
)

from fee_lab_to_nwb.scherrer_ophys.scherrerophysimagingextractorinterface import (
    ScherrerOphysImagingExtractorInterface,
)


class ScherrerOphysNWBConverter(NWBConverter):
    """Primary conversion class for the optical imaging data of the Fee lab."""

    data_interface_classes = dict(
        Movie=MovieInterface,
        Imaging=ScherrerOphysImagingExtractorInterface,
    )
