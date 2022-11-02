# fee-lab-to-nwb

NWB conversion scripts for the [Fee Lab at MIT](https://feelaboratory.org/) data to the
[Neurodata Without Borders](https://nwb-overview.readthedocs.io/) data format.

## Clone and install

To run the conversion some basic machinery is needed: **python, git and pip**.
For most users, we recommend you to
install `conda` ([installation instructions](https://docs.conda.io/en/latest/miniconda.html))
as it contains all the required machinery in a single and simple installation. If your
system
is windows you might also need to
install `git` ([installation instructions](https://github.com/git-guides/install-git))
to interact with this repository.

From a terminal (note that conda should install one in your system) you can do the
following:

```
git clone https://github.com/catalystneuro/fee-lab-to-nwb
cd fee-lab-to-nwb
conda env create --file make_conda_env.yml
conda activate fee_lab_to_nwb_env
```

This creates
a [conda environment](https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/environments.html)
which isolates the conversion from your system. We recommend that you run all your
conversion related tasks and analysis from that environment to minimize the
interference of this code with your own system.

Alternatively, if you want to avoid conda altogether (for example if you use another
virtual environment tool) you can install the repository with the following commands
using only pip:

```
git clone https://github.com/catalystneuro/fee-lab-to-nwb
cd fee-lab-to-nwb
pip install -e .
```

Note:
both of the methods above install the repository
in [editable mode](https://pip.pypa.io/en/stable/cli/pip_install/#editable-installs)

You can also install the latest release of the package with pip:
```
pip install fee-lab-to-nwb
```

## Repository structure

Each conversion is organized in a directory of its own in the `src` directory:

    fee-lab-to-nwb/
    ├── LICENSE
    ├── make_env.yml
    ├── pyproject.toml
    ├── README.md
    ├── requirements.txt
    ├── setup.py
    └── src
        ├── fee_lab_to_nwb
        │   ├── general_interfaces
        │   └── scherrer_ophys
        │       ├── convert_session.py
        │       ├── metadata.yml
        │       ├── notes.md
        │       ├── requirements.txt
        │       ├── scherrerophysimagingextractor.py
        │       ├── scherrerophysimaginginterface.py
        │       ├── scherrerophysnwbconverter.py
        │       └── __init__.py

        └── __init__.py

For the conversion `scherrer_ophys` you can find a directory located
in `src/fee-lab-to-nwb/scherrer_ophys`. Inside the conversion directory you can
find the following files:

* `convert_session.py`: this is the central script that you must run in order to perform the full conversion.
* `metadata.yml`: metadata in yaml format for this specific conversion.
* `notes.md`: notes and comments about the source data.
* `requirements.txt`: dependencies specific to this conversion.

The other files that are necessary this specific conversion:
* `scherrerophysimagingextractor.py`: the extractor for a single ophys file.
* `scherrerophysimaginginterface.py`:  the interface for this ophys dataset.
* `scherrerophysnwbconverter.py`: the place where the `NWBConverter` class is defined.

The directory might contain other files that are necessary for the conversion but those are the central ones.

## Running a specific conversion
To run a specific conversion, you might need to install first some conversion specific dependencies that are located in each conversion directory:
```
pip install -r src/fee_lab_to_nwb/scherrer_ophys/requirements.txt
```

You can run a specific conversion with the following command:
```
python src/fee_lab_to_nwb/scherrer_ophys/convert_session.py
```
Note that when installing `fee-lab-to-nwb` from `pip` the conversion script will be located
wherever `pip` installs site packages. In this case you will need to manually copy/paste usage scripts
to a location where you want to use them.

## Questions during a conversion
If you encounter any problems during the conversion, [open an issue](https://github.com/catalystneuro/fee-lab-to-nwb/issues/new), and we will
help you!
