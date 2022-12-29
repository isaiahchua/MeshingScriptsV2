## Installation

1. Setup virtual environment (miniconda/miniforge recommended)

2. Install prerequisites (vmtk, simpleitk)

        conda update conda
        conda config --set restore_free_channel true
        conda create -n foo -c conda-forge python=3.9
        conda activate foo
        conda install -c conda-forge numpy=1.22.3 vtk=9.1.0 itk=5.2.0 vmtk=1.5.0
        conda install -c conda-forge simpleitk

    **Note:** If you are using a Mac with the new Apple Silicon (e.g. M1), 
    you will have to create an environment that runs rosetta. 
    Run the following lines instead:

        conda update conda
        conda config --set restore_free_channel true
        CONDA_SUBDIR=osx-64 conda create -n foo_rosetta python=3.9
        conda activate foo_rosetta
        conda config --env --set subdir osx-64
        conda install -c conda-forge vtk=9.1.0 itk=5.2.0 vmtk=1.5.0
        conda install -c conda-forge simpleitk

    **Note:** If you are using Ubuntu/Linux you might experience the render
    window freezing when running the meshing scripts. If so please change the
    following lines in the vmtkrenderer.py file. 

    ![vmtkrenderer bef](assets/vmtkrenderer_bef.png)

    ![vmtkrenderer aft](assets/vmtkrenderer_aft.png)

    tip: find the vmtk folder by running this in your vmtk virtual environment

        python -c "from vmtk import vmtkscripts; print(vmtkscripts.__file__)"


3. Clone environment using Git 

        git clone https://github.com/isaiahchua/MeshingScriptsV2.git

## Python Scripts

**Tip:** For python scripts, run with ``-h`` flag to see additional options/help.

**view.py**

High-level wrapper for quickly viewing vessel centerlines, surfaces and meshes,
sample vessel provided in the "example_data" folder.

Example usage:
    
    python view.py -s example_data/demo_centerlines/aorta_cl.vtp example_data/ref_surface/aorta_clip.vtp

**meshing.py**

Workflow for creating a blood vessel mesh where element size is determined based
on the vessel size (adaptive). 

Example usage:

    python meshing.py -f example_data/demo_raw_surface/aorta.vtp

**meshing.sh**

Bash script that allow easy execution of common vmtk functions used to generate 
vessel volumetric meshes.

The script will ask for the parent directory of the input surface, the file path 
from the parent directory of the input surface, and the save path of the output 
file from the parent directory. 

After which input the number corresponding to the function you want to execute.

Example usage:

    bash meshing.sh

**convert_centerline_to_image.py**

Create an image file (".nii.gz") from a surface file using a reference image to 
set the origin and spacing of the image file. 

Example usage:

    python convert_centerline_to_image.py \
    ./example_data/demo_centerlines/aorta_cl.vtp \
    ./example_data/demo_centerlines/aorta_cl.nii.gz \
    ./example_data/ref_image/Aorta_voi.mha

**extract_multiple_centerlines.py**

Recursively search a parent directory for surfaces and create centerlines in a
mirror directory tree.

Example usage:

    python extract_multiple_centerlines.py -l ./example_data/demo_surface/log.csv \
    -c -w ./example_data/demo_surface/
