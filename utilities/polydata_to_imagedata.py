#! /usr/bin/env python3

#  Copyright (c) Thiago Franco de Moraes
#
#  This source code is licensed under the MIT license found in the
#  LICENSE file in the root directory of this source tree.

from time import time
import math
import sys
import numpy as np
import itk
import vtk
from vmtk import vtkvmtk

def GetImageProperties(image):
    size = list(itk.size(image))
    origin = list(itk.origin(image))
    spacing = list(itk.spacing(image))
    return size, origin, spacing

def ReadMeshFile(filename):
    if filename.lower().endswith(".stl"):
        reader = vtk.vtkSTLReader()
    elif filename.lower().endswith(".ply"):
        reader = vtk.vtkPLYReader()
    elif filename.lower().endswith(".vtp"):
        reader = vtk.vtkXMLPolyDataReader()
    else:
        raise ValueError("Only reads STL, VTP and PLY")
    reader.SetFileName(filename)
    reader.Update()
    return reader.GetOutput()

def CapSurface(polydata):
    surfaceCapper = vtkvmtk.vtkvmtkCapPolyData()
    surfaceCapper.SetDisplacement(0.)
    surfaceCapper.SetInPlaneDisplacement(0.)
    surfaceCapper.SetInputData(polydata)
    surfaceCapper.Update()
    return surfaceCapper.GetOutput()

class PolydataToImage:

    def __init__(self, polydata, dimensions=[], origin=[], spacing=[], padding=1):
        self.polydata = polydata
        self.dimensions = dimensions
        self.origin = origin
        self.spacing = spacing
        self.padding = padding
        self.bounds = polydata.GetBounds()
        self.image = None

        xi, xf, yi, yf, zi, zf = self.bounds
        if not self.spacing and self.dimensions:
            dx, dy, dz = dimensions
            sx = (xf - xi) / dx
            sy = (yf - yi) / dy
            sz = (zf - zi) / dz
            self.spacing = [sx, sy, sz]

        if self.spacing and not self.dimensions:
            sx, sy, sz = self.spacing
            dx = round((xf - xi) / sx)
            dy = round((yf - yi) / sy)
            dz = round((zf - zi) / sz)
            self.dimensions = [dx, dy, dz]

        if not self.origin:
            sx, sy, sz = self.spacing
            ox = xi + sx / 2.0
            oy = yi + sy / 2.0
            oz = zi + sz / 2.0
            self.origin = [ox, oy, oz]

        if self.padding:
            sx, sy, sz = self.spacing
            ox, oy, oz = self.origin
            ox -= sx * padding
            oy -= sy * padding
            oz -= sz * padding
            self.origin = [ox, oy, oz]
            dx, dy, dz = self.dimensions
            dx += 2 * padding
            dy += 2 * padding
            dz += 2 * padding
            self.dimensions = [dx, dy, dz]


    def Execute(self):
        polydata = CapSurface(self.polydata)

        dx, dy, dz = self.dimensions
        image = vtk.vtkImageData()
        image.SetSpacing(self.spacing)
        image.SetDimensions(self.dimensions)
        image.SetExtent(0, dx - 1, 0, dy - 1, 0, dz - 1)
        image.SetOrigin(self.origin)
        image.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)

        inval = 1
        outval = 0

        for i in range(image.GetNumberOfPoints()):
            image.GetPointData().GetScalars().SetTuple1(i, inval)

        pol2stenc = vtk.vtkPolyDataToImageStencil()
        pol2stenc.SetInputData(polydata)
        pol2stenc.SetInformationInput(image)
        pol2stenc.Update()

        imgstenc = vtk.vtkImageStencil()
        imgstenc.SetInputData(image)
        imgstenc.SetStencilConnection(pol2stenc.GetOutputPort())
        imgstenc.ReverseStencilOff()
        imgstenc.SetBackgroundValue(outval)
        imgstenc.Update()
        self.image = imgstenc.GetOutput()
        # direction_matrix = [-1., 0., 0., 0., -1., 0., 0., 0., 1.]
        # final_image.SetDirectionMatrix(direction_matrix)

    def Save(self, filename):
        writer = vtk.vtkXMLImageDataWriter()
        writer.SetFileName(filename)
        writer.SetInputData(self.image)
        writer.Write()

    def SaveNifti(self, filename):
        qmat = vtk.vtkMatrix4x4()
        qmat.Identity()
        qmat.SetElement(0, 0, -1)
        qmat.SetElement(1, 1, -1)
        writer = vtk.vtkNIFTIImageWriter()
        writer.SetFileName(filename)
        writer.SetInputData(self.image)
        writer.SetQFormMatrix(qmat)
        qmat = writer.GetQFormMatrix()
        writer.Write()

def main():
    input_filename = sys.argv[1]
    output_filename = sys.argv[2]
    output_filetype = output_filename.split(".", 1)[-1]
    if len(sys.argv) == 4:
        ref_filename = sys.argv[3]
        refImage = itk.imread(ref_filename)
        size, origin, spacing = GetImageProperties(refImage)
    else:
        size, origin, spacing = None, (0.5, 0.5, 0.5), None

    polydata = ReadMeshFile(input_filename)

    converter = PolydataToImage(polydata, size, origin, spacing, padding=1)
    converter.Execute()

    if output_filetype == "vti":
        converter.Save(output_filename)
    elif output_filetype in ["nii", "nii.gz"]:
        converter.SaveNifti(output_filename)
    else:
        raise Exception("Invalid file extension")


if __name__ == "__main__":
    main()
