import os
from time import time
import pickle
import numpy as np
import vtk
from vmtk import vtkvmtk
from vmtk import vmtkscripts
from .visualize import Visualize


class Surface:
    def __init__(self):
        self.surface = None
        self.prev_surface = None
        self.sfarray = None
        self.sfdict = {
            "Points": None,
            "PointData": dict(),
            "CellData": {"CellPointIds": None},
        }
        self.centerlines = None
        self.dimensions = None
        self.origin = None

    def load(self, sfpath, clpath=None):
        sfreader = vmtkscripts.vmtkSurfaceReader()
        sfreader.InputFileName = sfpath
        sfreader.Execute()
        self.surface = sfreader.Surface
        if self.surface == None:
            raise ValueError("No surface.")
        if clpath != None:
            clreader = vmtkscripts.vmtkSurfaceReader()
            clreader.InputFileName = clpath
            clreader.Execute()
            self.centerlines = clreader.Surface

    def set_image_dimensions(self, dims):
        self.dimensions = dims

    def set_image_origin(self, pt):
        self.origin = pt

    def restore(self):
        self.surface = self.prev_surface
        print("surface restored")

    def view(self):
        viewer = Visualize(surface=self.surface, centerlines=self.centerlines)
        viewer.view_surface()

    def cap(self):
        sfcapper = vmtkscripts.vmtkSurfaceCapper()
        sfcapper.Surface = self.surface
        sfcapper.Execute()
        self.surface = sfcapper.Surface

    def smooth(self):
        self.prev_surface = self.surface
        kite_rm = vmtkscripts.vmtkSurfaceKiteRemoval()
        kite_rm.Surface = self.surface
        kite_rm.Execute()
        sfsmoother = vmtkscripts.vmtkSurfaceSmoothing()
        sfsmoother.NumberOfIterations = 30
        sfsmoother.PassBand = 0.1
        sfsmoother.Surface = kite_rm.Surface
        sfsmoother.Execute()
        self.surface = sfsmoother.Surface
        viewer = Visualize(surface=self.surface)
        viewer.view_surface()

    def clip(self, method="manual"):
        self.prev_surface = self.surface
        if method == "manual":
            sfclipper = vmtkscripts.vmtkSurfaceClipper()
            sfclipper.Surface = self.surface
            sfclipper.Execute()
            self.surface = sfclipper.Surface
        elif method == "auto":
            if self.centerlines == None:
                raise ValueError(
                    "No centerlines provided. Note: centerlines should be endpoint extracted."
                )
            sfendextractor = vmtkscripts.vmtkEndpointExtractor()
            sfendextractor.NumberOfEndpointSpheres = 1
            sfendextractor.Centerlines = self.centerlines
            sfendextractor.Execute()
            sfbranchclipper = vmtkscripts.vmtkBranchClipper()
            sfbranchclipper.Surface = self.surface
            sfbranchclipper.Centerlines = sfendextractor.Centerlines
            sfbranchclipper.Execute()
            sfconnectivity = vmtkscripts.vmtkSurfaceConnectivity()
            sfconnectivity.CleanOutput = 1
            sfconnectivity.Surface = sfbranchclipper.Surface
            sfconnectivity.Execute()
            self.surface = sfconnectivity.Surface
        viewer = Visualize(surface=self.surface, surface2=self.prev_surface)
        viewer.view_surface()

    def extend(self, method="cl", ratio=10.0, interact=0):
        self.prev_surface = self.surface
        sfflowextend = vmtkscripts.vmtkFlowExtensions()
        sfflowextend.AdaptiveExtensionLength = 1
        sfflowextend.ExtensionRatio = ratio
        if method == "cl":
            sfflowextend.ExtensionMode = "centerlinedirection"
        elif method == "bn":
            sfflowextend.ExtensionMode = "boundarynormal"
        else:
            raise ValueError("Invalid method")
        sfflowextend.Interactive = interact
        sfflowextend.Surface = self.surface
        sfflowextend.Centerlines = self.centerlines
        sfflowextend.Execute()
        sfconnectivity = vmtkscripts.vmtkSurfaceConnectivity()
        sfconnectivity.CleanOutput = 1
        sfconnectivity.Surface = sfflowextend.Surface
        sfconnectivity.Execute()
        sftriangle = vmtkscripts.vmtkSurfaceTriangle()
        sftriangle.Surface = sfconnectivity.Surface
        sftriangle.Execute()
        self.surface = sftriangle.Surface
        viewer = Visualize(surface=self.surface)
        viewer.view_surface()

    def resurf(self, method="cellarea"):
        self.prev_surface = self.surface
        if method == "cellarea":
            sfremeshsurf = vmtkscripts.vmtkSurfaceRemeshing()
            sfremeshsurf.TargetArea = 0.1
            sfremeshsurf.MinAreaFactor = 0.2
            sfremeshsurf.Surface = self.surface
            sfremeshsurf.Execute()
        elif method == "adaptive":
            disttocl = vmtkscripts.vmtkDistanceToCenterlines()
            disttocl.UseRadiusInformation = 1
            disttocl.Surface = self.surface
            disttocl.Centerlines = self.centerlines
            disttocl.Execute()
            sfremeshsurf = vmtkscripts.vmtkSurfaceRemeshing()
            sfremeshsurf.ElementSizeMode = "edgelengtharray"
            sfremeshsurf.TargetEdgeLengthArrayName = "DistanceToCenterlines"
            sfremeshsurf.TargetEdgeLengthFactor = 0.3
            sfremeshsurf.Surface = disttocl.Surface
            sfremeshsurf.Centerlines = disttocl.Centerlines
            sfremeshsurf.Execute()
        else:
            raise ValueError("Invalid method")
        sftriangle = vmtkscripts.vmtkSurfaceTriangle()
        sftriangle.Surface = sfremeshsurf.Surface
        sftriangle.Execute()
        self.surface = sftriangle.Surface
        viewer = Visualize(surface=self.surface)
        viewer.view_surface()

    def export_cl(self, savepath):
        clwriter = vmtkscripts.vmtkSurfaceWriter()
        clwriter.OutputFileName = savepath
        clwriter.Format = "vtk"
        clwriter.Surface = self.centerlines
        clwriter.Execute()

    def convert_to_array(self):
        if self.surface == None:
            raise ValueError("No surface.")
        sfNumpyAdaptor = vmtkscripts.vmtkSurfaceToNumpy()
        sfNumpyAdaptor.Surface = self.surface
        sfNumpyAdaptor.Execute()
        self.sfarray = sfNumpyAdaptor.ArrayDict

    def convert_to_dict(self):
        if self.sfarray == None:
            raise ValueError(
                "use convert_to_array method create an ArrayDict from the loaded surface."
            )
        self.sfdict["Points"] = self.sfarray["Points"]
        if isinstance(self.sfarray["PointData"], type(self.sfarray)):
            for key in self.sfarray["PointData"].keys():
                self.sfdict["PointData"][key] = self.sfarray["PointData"][key]
        for key in self.sfarray["CellData"].keys():
            self.sfdict["CellData"][key] = self.sfarray["CellData"][key]

    def convert_to_image(self):
        bounds = self.surface.GetBounds()
        surfaceCapper = vtkvmtk.vtkvmtkCapPolyData()
        surfaceCapper.SetDisplacement(0.)
        surfaceCapper.SetInPlaneDisplacement(0.)
        surfaceCapper.SetInputData(self.surface)
        surfaceCapper.Update()
        start = time()
        converter = vtk.vtkVoxelModeller()
        converter.SetModelBounds(bounds)
        converter.SetSampleDimensions(self.dimensions)
        converter.SetScalarTypeToFloat()
        converter.SetInputConnection(surfaceCapper.GetOutputPort())
        converter.Update()
        img = converter.GetOutput()
        end = time()
        print(f"Time taken: {end - start} s.")
        print(img)

    def save_dict(self, savepath):
        if self.sfdict == None:
            raise ValueError(
                "use convert_to_dict method to create a nested dictionary of numpy arrays."
            )
        if not os.path.isdir(os.path.dirname(savepath)):
            os.makedirs(os.path.dirname(savepath))
        with open(savepath, "wb") as f:
            pickle.dump(self.sfdict, f)
        print("surface nested dictionary saved.")

    def save_points(self, savepath):
        if self.sfarray == None:
            raise ValueError(
                "use convert_to_array method create an ArrayDict from the loaded centerlines."
            )
        if not os.path.isdir(os.path.dirname(savepath)):
            os.makedirs(os.path.dirname(savepath))
        np.save(savepath, self.sfarray["Points"])
        print("point array saved.")

    def save_surface(self, savepath):
        if not os.path.isdir(os.path.dirname(savepath)):
            os.makedirs(os.path.dirname(savepath))
        sfwriter = vmtkscripts.vmtkSurfaceWriter()
        sfwriter.OutputFileName = savepath
        sfwriter.Surface = self.surface
        sfwriter.Execute()


if __name__ == "__main__":
    pass
