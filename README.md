# Title



![CI](https://github.com/MannLabs/alphapept/workflows/CI/badge.svg)
![Quick Test](https://github.com/MannLabs/alphapept/workflows/Quick%20Test/badge.svg)
![Performance test](https://github.com/MannLabs/alphapept/workflows/Performance%20test/badge.svg)
![Windows Installer](https://github.com/MannLabs/alphapept/workflows/Windows%20Installer/badge.svg)

# AlphaPept
<img src="nbs\images\alphapept_logo.png" align="center">

 > A modular, python-based framework to analyze mass spectrometry data. Powered by nbdev. Supercharged with numba.


## Documentation

The documentation is automatically built based on the jupyter notebooks (nbs/index.ipynb) and can be found [here](https://mannlabs.github.io/alphapept/):

## Installation Instructions


### Python

We highly recommend the [Anaconda](https://www.anaconda.com) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) Python distribution, which comes with a powerful package manager. See below for additional instructions for Linux and Mac as they require additional installation of Mono to use the RawFileReader.

It is strongly recommended to install AlphaPept in its own environment.
1. Open the console and create a new conda environment: `conda create --name alphapept python=3`
2. Activate the environment: `conda activate alphapept`
3. Redirect to the folder of choice and clone the repository: `git clone https://github.com/MannLabs/alphapept.git`
4. Navigate to the alphapept folder and install the package with `pip install .` (default users) or with `pip install -e .` to enable developers mode.

If AlphaPept is installed correctly, you should be able to import Alphapept as a package within the environment; see below.
{% include note.html content='If you would like to use alphapept in your jupyter notebook environment, additionally install nb_conda: `conda install nb_conda`. This also installs the jupyter notebook extensions. They can be called from a running jupyter instance like so: `http://localhost:8888/nbextensions`. For navigating the notebooks, the exension `collapsible headings` and `toc2` are very beneficial. For developing with the notebooks, see the `nbev` section below.' %}

#### Linux

1. Install the build-essentials: `sudo apt-get install build-essential`
2. Install Mono from mono-project website [Mono Linux](https://www.mono-project.com/download/stable/#download-lin)
3. Navigate to the alphapept folder and install the package with `pip install .` (default users) or with `pip install -e .` to enable developers mode.


#### Mac

1. Install [brew](https://brew.sh) and pkg-config: `brew install pkg-config`
2. Intall Mono from mono-project website [Mono Mac](https://www.mono-project.com/download/stable/)
3. Register the Mono-Path to your system:
For macOS Catalina, open the configuration of zsh via the terminal:
* Type in `cd` to navigate to the home directory.
* Type `nano ~/.zshrc` to open the configuration of the terminal
* Add the path to your mono installation: `export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig:/usr/lib/pkgconfig:/Library/Frameworks/Mono.framework/Versions/6.12.0/lib/pkgconfig:$PKG_CONFIG_PATH`. Make sure that the Path matches to your version (Here 6.12.0)
* Save everything and execute `. ~/.zshrc` 
4. Navigate to the alphapept folder and install the package with `pip install .` (default users) or with `pip install -e .` to enable developers mode.


### Standalone Windows Installer
To use AlphaPept as a stand-alone program for end-users, it can be installed on Windows machines via a one-click installer. Download the latest version [here](http://alphapept.org).


### Additional Notes
> To access Thermo files, we have integrated [RawFileReader](https://planetorbitrap.com/rawfilereader) into AlphaPept. We rely on [Mono](https://www.mono-project.com/) for Linux/Mac systems.

 > To access Bruker files, we rely on the `timsdata`-library. Currently, only Windows is supported. For feature finding, we use the Bruker Feature Finder, which can be found in the `ext` folder of this repository.

## How to use

AlphaPept is meant to be a framework to implement and test new ideas quickly but also to serve as a performant processing pipeline. In principle, there are three use-cases:

* GUI: Use the graphical user interface to select settings and process files manually.
* CMD: Use the command-line interface to process files. Useful when building automatic pipelines.
* Python: Use python modules to build individual workflows. Useful when building customized pipelines and using Python as a scripting language or when implementing new ideas. 

### Windows Standalone Installation

For the windows installation, simply click on the shortcut after installation. The windows installation also installs the command-line tool so that you can call alphapept via `alphapept` in the command line.

### Python Package

Once AlphaPept is correctly installed, you can use it like any other python module.

```
from alphapept.fasta import get_frag_dict, parse
from alphapept import constants

peptide = 'PEPT'

get_frag_dict(parse(peptide), constants.mass_dict)
```




    {'b1': 98.06004032687,
     'b2': 227.10263342686997,
     'b3': 324.15539728686997,
     'y1': 120.06551965033,
     'y2': 217.11828351033,
     'y3': 346.16087661033}



### Using as a tool

If alphapept is installed an a conda or virtual environment, launch this environment first.

To launch the command line interface use:
* `alphapept`

This allows us to select different modules. To start the GUI use:
* `alphapept gui`

Likewise, to start the watcher use:
* `alphapept watcher`
> AlphaPept has a watcher module that continuously monitors a target folder and automatically performs file conversion and feature finding on new files.

To run a workflow, use:* `alphapept workflow your_own_workflow.yaml`An example workflow is easily generated by running the GUI once and saving the settings which an be modified on e per-project basis.

## Analyzing an experiment
This describes the minimal steps to analyze an experiment.

### GUI

1. Open the GUI. Drag and drop experimental files and at least one fasta in the `Experiment` tab. 
2. Default settings are loaded and can be changed or saved in the `Settings` tab
3. Navigate to the Run panel and click `Start`

### Investigating the result files
The experimental results will be stored in the corresponding *.hdf-files.

### CMD / Python
1. Create a settings-file. This can be done by changing the `default_settings.yaml` in the repository or using the GUI.
2. Run the analysis with the new settings file. `alphapept run new_settings.yaml`

Within Python (i.e., Jupyter notebook) the following code would be required)
```
from alphapept.settings import load_settings
from alphapept.runner import run_alphapept
settings = load_settings('new_settings.yaml')
r = run_alphapept(settings)
```

## Contributing
If you have a feature request or a bug report, please post it as an issue on the GitHub issue tracker. If you want to contribute, put a PR for it. You can find more guidelines for contributing and how to get started [here](https://github.com/MannLabs/alphapept/blob/master/CONTRIBUTING.md). I will gladly guide you through the codebase and credit you accordingly. Additionally, you can check out the Projects-page on GitHub. You can also contact me via opensource@alphapept.com.
