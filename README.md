## Installation

a. Setup virtual environment (miniconda/miniforge recommended)

b. install prerequisites (vmtk, simpleitk)

    `conda update conda`
    `conda config --set restore_free_channel true`
    `conda create -n foo -c conda-forge python=3.9`
    `conda activate foo`
    `conda install -c conda-forge vtk=9.1.0 itk=5.2.0 vmtk=1.5.0`
    `conda install -c conda-forge simpleitk`

    Note: If you are using a Mac with the new Apple Silicon (e.g. M1), 
    you will have to create an environment that runs rosetta. 
    Run the following lines instead:

    `conda update conda`
    `conda config --set restore_free_channel true`
    `CONDA_SUBDIR=osx-64 conda create -n foo_rosetta python=3.9`
    `conda activate foo_rosetta `
    `conda config --env --set subdir osx-64`
    `conda install -c conda-forge vtk=9.1.0 itk=5.2.0 vmtk=1.5.0`
    `conda install -c conda-forge simpleitk`

c. Clone environment using Git 

    `git clone https://github.com/isaiahchua/MeshingScriptsV2.git`

## Commands
