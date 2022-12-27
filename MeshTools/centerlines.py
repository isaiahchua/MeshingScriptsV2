import os
import pickle
import numpy as np
from vmtk import vmtkscripts
from .visualize import Visualize
from .vmtkcenterlinesnetwork2 import vmtkCenterlinesNetwork2


class Centerlines:
    def __init__(self):
        self.surface = None
        self.centerlines = None
        self.clarray = None
        self.cldict = {
            "Points": None,
            "PointData": {},
            "CellData": {"CellPointIds": None}
        }
        self.renderer = None

    def load(self, clpath=None, sfpath=None):
        if (clpath == None) and (sfpath == None):
            raise ValueError("No centerlines or surface.")
        if clpath != None:
            clreader = vmtkscripts.vmtkSurfaceReader()
            clreader.InputFileName = clpath
            clreader.Execute()
            self.centerlines = clreader.Surface
            if self.centerlines == None:
                raise ValueError("No centerlines produced")
        if sfpath != None:
            sfreader = vmtkscripts.vmtkSurfaceReader()
            sfreader.InputFileName = sfpath
            sfreader.Execute()
            self.surface = sfreader.Surface

    def restore(self):
        self.centerlines = self.prev_centerlines
        print("Centerlines restored")

    def view(self, ptdata=None, celldata=None):
        viewer = Visualize(surface=self.surface, centerlines=self.centerlines)
        viewer.view_centerlines(ptarray=ptdata, cellarray=celldata)

    def create_cl(self, method="pickpoints", seed=None):
        self.prev_centerlines = self.centerlines
        if method == "pickpoints":
            clcreator = vmtkscripts.vmtkCenterlines()
            clcreator.Surface = self.surface
            clcreator.Execute()
        elif method == "openprofiles":
            clcreator = vmtkscripts.vmtkCenterlines()
            clcreator.SeedSelectorName = "openprofiles"
            clcreator.AppendEndPoints = 1
            clcreator.Surface = self.surface
            clcreator.Execute()
        elif method == "clnet":
            clcreator = vmtkscripts.vmtkCenterlinesNetwork()
            clcreator.RandomSeed = seed
            clcreator.Surface = self.surface
            # clcreator.UseJoblib = True
            clcreator.Execute()
        else:
            raise ValueError("Invalid method")
        self.centerlines = clcreator.Centerlines
        viewer = Visualize(centerlines=self.centerlines, surface=self.surface)
        viewer.view_centerlines()

    def create_cl2(self):
        self.prev_centerlines = self.centerlines
        clcreator = vmtkCenterlinesNetwork2()
        clcreator.AppendOpenEnds = 1
        clcreator.Surface = self.surface
        clcreator.Execute()
        self.centerlines = clcreator.Centerlines
        viewer = Visualize(centerlines=self.centerlines, surface=self.surface)
        viewer.view_centerlines()

    def convert_to_array(self):
        if self.centerlines == None:
            raise ValueError("No centerlines.")
        clNumpyAdaptor = vmtkscripts.vmtkCenterlinesToNumpy()
        clNumpyAdaptor.Centerlines = self.centerlines
        clNumpyAdaptor.Execute()
        self.clarray = clNumpyAdaptor.ArrayDict

    def convert_to_dict(self):
        if self.clarray == None:
            raise ValueError(
                "use convert_to_array method create an ArrayDict from the loaded centerlines."
            )
        self.cldict["Points"] = self.clarray["Points"]
        if isinstance(self.clarray["PointData"], type(self.clarray)):
            for key in self.clarray["PointData"].keys():
                self.cldict["PointData"][key] = self.clarray["PointData"][key]
        for key in self.clarray["CellData"].keys():
            self.cldict["CellData"][key] = self.clarray["CellData"][key]

    def convert_to_cl(self):
        if self.clarray == None:
            raise ValueError(
                "use convert_to_array method create an ArrayDict from the loaded centerlines."
            )
        clNumpyAdaptor = vmtkscripts.vmtkNumpyToCenterlines()
        clNumpyAdaptor.ArrayDict = self.clarray
        clNumpyAdaptor.Execute()
        self.centerlines = clNumpyAdaptor.Centerlines

    def add_cell_labels(self):
        if self.clarray == None:
            raise ValueError("No ArrayDict")
        n = len(self.clarray["CellData"]["CellPointIds"])
        cell_labels = np.array([i for i in range(n)])
        self.clarray["CellData"]["CellLabels"] = cell_labels
        self.convert_to_cl()

    def extract_branches(self):
        self.prev_centerlines = self.centerlines
        brextractor = vmtkscripts.vmtkBranchExtractor()
        brextractor.RadiusArrayName = "MaximumInscribedSphereRadius"
        brextractor.Centerlines = self.centerlines
        brextractor.Execute()
        self.centerlines = brextractor.Centerlines

    def extract_endpts(self, num_eps=1, num_gs=1):
        self.prev_centerlines = self.centerlines
        epextractor = vmtkscripts.vmtkEndpointExtractor()
        epextractor.RadiusArrayName = "MaximumInscribedSphereRadius"
        epextractor.NumberOfEndpointSpheres = num_eps
        epextractor.NumberOfGapSpheres = num_gs
        epextractor.Centerlines = self.centerlines
        epextractor.Execute()
        self.centerlines = epextractor.Centerlines

    def update_groupids(self):
        # untested function, can look at vmtkCenterlineMerge as well for clipping of flow extensions
        self.prev_centerlines = self.centerlines
        clupdater = vmtkscripts.vmtkCenterlineLabeller()
        clupdater.Centerlines = self.centerlines
        clupdater.Execute()

    def save_centerlines(self, savepath):
        if not os.path.isdir(os.path.dirname(savepath)):
            os.makedirs(os.path.dirname(savepath))
        clwriter = vmtkscripts.vmtkSurfaceWriter()
        clwriter.OutputFileName = savepath
        clwriter.Surface = self.centerlines
        clwriter.Execute()

    def save_dict(self, savepath):
        if self.cldict == None:
            raise ValueError(
                "use convert_to_dict method to create a nested dictionary of numpy arrays."
            )
        if not os.path.isdir(os.path.dirname(savepath)):
            os.makedirs(os.path.dirname(savepath))
        with open(savepath, "wb") as f:
            pickle.dump(self.cldict, f)
        print("nested dictionary saved.")

    def save_points(self, savepath):
        if self.clarray == None:
            raise ValueError(
                "use convert_to_array method create an ArrayDict from the loaded centerlines."
            )
        if not os.path.isdir(os.path.dirname(savepath)):
            os.makedirs(os.path.dirname(savepath))
        np.save(savepath, self.clarray["Points"])
        print("point array saved.")


if __name__ == "__main__":
    pass
