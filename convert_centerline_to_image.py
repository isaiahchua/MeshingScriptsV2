import sys, os
import argparse
import vtk
from vmtk import vmtkscripts
import numpy as np
import SimpleITK as sitk
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D

# %matplotlib notebook

def ResampleCenterlines(centerlinePolyData, resamplingDistance):
    resampler = vmtkscripts.vmtkLineResampling()
    resampler.Surface = centerlinePolyData
    resampler.Length = resamplingDistance
    resampler.Execute()
    return resampler.Surface

def convertPatient2ImageCoords(pts, origin, spacing):
    return np.round((pts + origin)/spacing).astype(np.int)

def main(clPath, savePath, imgPath):

    clReader = vmtkscripts.vmtkSurfaceReader()
    clReader.InputFileName = clPath
    clReader.Execute()
    cl = ResampleCenterlines(clReader.Surface, 2)

    clNumpyAdaptor = vmtkscripts.vmtkCenterlinesToNumpy()
    clNumpyAdaptor.Centerlines = cl
    clNumpyAdaptor.Execute()
    clArray = clNumpyAdaptor.ArrayDict
    clPoints = clArray["Points"]

    print("\nReading reference image...")
    sfImage = sitk.ReadImage(imgPath)
    origin = np.asarray([sfImage.GetOrigin()] * clPoints.shape[0])
    spacing = np.asarray([sfImage.GetSpacing()] * clPoints.shape[0])
    imgArray = sitk.GetArrayFromImage(sfImage)
    clCoords = np.zeros_like(imgArray).astype(np.uint8)

    clx, cly, clz = convertPatient2ImageCoords(clPoints, origin, spacing).T
    clCoords[clz, cly, clx] = 1
    direction_matrix = np.array([1., 0., 0. , 0., 1., 0., 0., 0., 1.])

    print("\nSaving centerline image...")
    clImage = sitk.GetImageFromArray(clCoords)
    clImage.SetOrigin(origin[0])
    clImage.SetSpacing(spacing[0])
    clImage.SetDirection(direction_matrix)
    imgWriter = sitk.ImageFileWriter()
    imgWriter.SetFileName(savePath)
    imgWriter.Execute(clImage)

    print("\nCenterline successfully converted.")
    return

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=
                "Convert centerlines from polydata to Nifti format using a reference image file for origin and spacing information.")
    parser.add_argument("src", metavar="SRC", type=str, default=None,
                        help="The parent directory where the surfaces are stored.")
    parser.add_argument("dest", metavar="DEST", type=str, default=None,
                        help="Path to save converted centerlines file in .nii.gz format.")
    parser.add_argument("ref", metavar="REF", type=str, default=None,
                        help="Path to reference image file.")
    args = parser.parse_args()

    clPath = args.src
    savePath = args.dest
    imgPath = args.ref

    main(clPath, savePath, imgPath)
