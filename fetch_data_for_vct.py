import sys, os
import shutil
import numpy as np
import pandas as pd
# from ImageTools import Image
from utilities import PolydataToImage, GetImageProperties, ReadMeshFile


# def split_and_move_labelled_images(parentdir, destdir):
    # if (parentdir[-1] != '/') or (destdir[-1] != '/'):
        # raise ValueError("parentdir or destdir must end with '/'.")
    # for directory in os.listdir(parentdir):
        # if os.path.isdir(parentdir + directory):
            # os.chdir(parentdir + directory)
        # for file in os.listdir(directory):
            # splitter = Image()
            # splitter.load(file)
            # splitter.convert_to_array()
            # splitter.save_labels(destdir, directory)

def move_to_single_directory(parentdir, destdir):
    if (parentdir[-1] != '/') or (destdir[-1] != '/'):
        raise ValueError("parentdir or destdir must end with '/'.")
    for directory in os.listdir(parentdir):
        if os.path.isdir(parentdir + directory):
            os.chdir(parentdir + directory)
        for file in os.listdir():
            vessel_id = file[-5:]
            newname = destdir + directory + '_' + vessel_id
            os.rename(file, newname)

def copy_surface_to_dest(paths, destdir, label, replace=False, sfPaths=None):
    if destdir[-1] != "/":
        destdir += "/"
    if label[-1] != "/":
        label += "/"
    if not os.path.isdir(destdir + label):
        os.makedirs(destdir + label)

    print(f"Copying files to {destdir + label}...", end=" ")
    for pth in paths:
        patientName = pth.split("/")[-3]
        vesselName = pth.split(".", 1)[0]
        if vesselName[-1].isnumeric():
            vesselId = vesselName[-1]
        else:
            vesselId = vesselName[-2]
        extension = "." + pth.split(".", 1)[1]
        dest = destdir + label + patientName + "_" + vesselId + extension
        if sfPaths != None:
            sfPaths.append(dest)
        if not replace:
            if os.path.exists(dest):
                print(f"{dest} exists!")
                continue
        shutil.copyfile(pth, dest)
    print("Done!")

def copy_centerline_to_dest(paths, destdir, label, replace=False, clPaths=None):
    if destdir[-1] != "/":
        destdir += "/"
    if label[-1] != "/":
        label += "/"
    if not os.path.isdir(destdir + label):
        os.makedirs(destdir + label)

    print(f"Copying files to {destdir + label}...", end=" ")
    for pth in paths:
        patientName = pth.split("/")[-3]
        vesselName = pth.split(".", 1)[0]
        if vesselName[-4].isnumeric():
            vesselId = vesselName[-4]
        else:
            vesselId = vesselName[-5]
        extension = "." + pth.split(".", 1)[1]
        dest = destdir + label + patientName + "_" + vesselId + extension
        if  clPaths != None:
            clPaths.append(dest)
        if not replace:
            if os.path.exists(dest):
                print(f"{dest} exists!")
                continue
        shutil.copyfile(pth, dest)
    print("Done!")

def create_images_from_surface(sfPaths, destdir, label, replace):
    if destdir[-1] != "/":
        destdir += "/"
    if label[-1] != "/":
        label += "/"
    if not os.path.isdir(destdir + label):
        os.makedirs(destdir + label)
    for file in sfPaths:
        splitFile = file.split(".", 1)
        if splitFile[1] == "vtp":
            vesselName = os.path.basename(splitFile[0])
            print(f"Creating {vesselName + '.nii.gz'}...", end=" ")
            savepath = destdir + label + vesselName + ".nii.gz"
            if os.path.exists(savepath) and not replace:
                print("File already exists!")
                continue
            polydata  = ReadMeshFile(file)
            converter = PolydataToImage(polydata, spacing=[0.5, 0.5, 0.5], padding=2)
            converter.Execute()
            converter.SaveNifti(savepath)
            print("Done!")


if __name__ == '__main__':

    successFile = sys.argv[1]
    destination = sys.argv[2]
    vesselTypeLabel = sys.argv[3]
    if len(sys.argv) == 5:
        replace = int(sys.argv[4])
        if replace != 0 and replace != 1:
            raise Exception("Invalid argument for replace")
    else:
        replace = False
    sfPaths = []
    sfDest = os.path.join(destination, "surface_polydata/")
    clDest = os.path.join(destination, "centerlines_polydata/")
    sfImageDest = os.path.join(destination, "surface_imagedata/")

    df = pd.read_csv(successFile, sep="\t", header=None)
    paths = df.iloc[:, 0]
    clPaths = [path.split(".", 1)[0] + "_cl.vtp" for path in paths]
    copy_surface_to_dest(paths, sfDest, vesselTypeLabel, replace, sfPaths)
    copy_centerline_to_dest(clPaths, clDest, vesselTypeLabel, replace)
    create_images_from_surface(sfPaths, sfImageDest, vesselTypeLabel, replace)


