# Upcoming

### Fixes
* Add auditory data to the NWB file as stimulus instead of acquisition. [PR #37](https://github.com/catalystneuro/fee-lab-to-nwb/pull/37)
* Removed "conversion", "starting_time" and "rate" key pops from TimeSeries metadata schema when
  constructing the metadata schema for `AudioInterface`. [PR #49](https://github.com/catalystneuro/fee-lab-to-nwb/pull/49)

### Improvements
* Create file for tracking changes. [PR #36](https://github.com/catalystneuro/fee-lab-to-nwb/pull/36)
* Changed the `MotifInterface` to take a second argument that corresponds the file
  that contains the Audio and SpikeGLX timestamps. This file is used for synchronizing
  the motif timestamps. [PR #33](https://github.com/catalystneuro/fee-lab-to-nwb/pull/33)
* Adjusted `session_start_time` for ophys to reference the first time entry from imaging timestamps. [PR #43](https://github.com/catalystneuro/fee-lab-to-nwb/pull/43)

### Features
* The `ScherrerOphysSegmentationInterface` is modified to write the configurations
  from EXTRACT segmentation to the NWB File. [PR #42](https://github.com/catalystneuro/fee-lab-to-nwb/pull/42)

### Testing
* Added auto-detector workflow for CHANGELOG.md updates. [PR #41](https://github.com/catalystneuro/fee-lab-to-nwb/pull/41)

# v1.0.0

* The first release of fee-lab-to-nwb. [PR #31](https://github.com/catalystneuro/fee-lab-to-nwb/pull/31)
