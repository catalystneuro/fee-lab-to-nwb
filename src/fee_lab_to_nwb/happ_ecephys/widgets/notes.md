### Visualizations for motifs and auditory data in Jupyter Notebook

Load the NWB file with `NWBHDF5IO`.
```python
from pynwb import NWBHDF5IO
io = NWBHDF5IO("7635_210729_LH_NCM.nwb", mode="r", load_namespaces=True)
nwbfile = io.read()
```

#### Standalone widgets
Use `MotifSoundCombinedWidget` to use a slider for interactively scrolling through the
recording and a button for changing the duration of the sound that is being shown.
Use the `figsize` argument to change the size of the figure.

```python
from fee_lab_to_nwb.happ_ecephys.widgets import MotifSoundCombinedWidget

MotifSoundCombinedWidget(nwbfile.stimulus["AcousticWaveformSeries"], figsize=(10, 10))
```
#### Using nwbwidgets
When using `nwb2widget` with an NWB file that is read from disk, make sure to have
`load_widgets` imported within the same Jupyter cell where your data is being loaded.

```python
from pynwb import NWBHDF5IO
from fee_lab_to_nwb.happ_ecephys.widgets import load_widgets
from nwbwidgets import nwb2widget

load_widgets()

io = NWBHDF5IO("7635_210729_LH_NCM.nwb", mode="r", load_namespaces=True)
nwbfile = io.read()

nwb2widget(nwbfile)
```
