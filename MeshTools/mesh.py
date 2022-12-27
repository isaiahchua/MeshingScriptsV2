import os
import pickle
import numpy as np
from vmtk import vmtkscripts
from .visualize import Visualize


class Mesh:
    def __init__(self):
        self.mesh = None
        self.surface = None
        self.centerlines = None
        self.prev_mesh = None
        self.meshsurface = None

    def load(self, mpath=None, sfpath=None, clpath=None):
        if mpath != None:
            mreader = vmtkscripts.vmtkMeshReader()
            mreader.InputFileName = mpath
            mreader.Execute()
            self.mesh = mreader.Mesh
        if sfpath != None:
            sfreader = vmtkscripts.vmtkSurfaceReader()
            sfreader.InputFileName = sfpath
            sfreader.Execute()
            self.surface = sfreader.Surface
        if clpath != None:
            clreader = vmtkscripts.vmtkSurfaceReader()
            clreader.InputFileName = clpath
            clreader.Execute()
            self.centerlines = clreader.Surface

    def restore(self):
        self.mesh = self.prev_mesh

    def view(self):
        viewer = Visualize(mesh=self.mesh)
        viewer.view_mesh()

    def view_comparison(self):
        viewer = Visualize(mesh=self.mesh, mesh2=self.prev_mesh)
        viewer.view_mesh()

    def clip(self, method="manual", cl=None):
        self.prev_mesh = self.mesh
        if method == "manual":
            mclipper = vmtkscripts.vmtkMeshClipper()
            mclipper.Mesh = self.mesh
            mclipper.Execute()
            self.mesh = mclipper.Mesh
        elif method == "auto":
            if cl == None:
                raise ValueError(
                    "No centerlines provided. Note: centerlines should be endpoint extracted."
                )
            mbranchclipper = vmtkscripts.vmtkMeshBranchClipper()
            mbranchclipper.Interactive = 1
            mbranchclipper.Mesh = self.mesh
            mbranchclipper.Centerlines = cl
            mbranchclipper.Execute()
            self.mesh = mbranchclipper.Mesh
        self.view_comparison()

    def create_mesh(self, method="edgelength"):
        self.prev_mesh = self.mesh
        if method == "edgelength":
            mesher = vmtkscripts.vmtkMeshGenerator()
            mesher.TargeEdgeLength = 0.2
            mesher.Surface = self.surface
            mesher.Execute()
        elif method == "adaptive":
            disttocl = vmtkscripts.vmtkDistanceToCenterlines()
            disttocl.UseRadiusInformation = 1
            disttocl.Surface = self.surface
            disttocl.Centerlines = self.centerlines
            disttocl.Execute()
            mesher = vmtkscripts.vmtkMeshGenerator()
            mesher.ElementSizeMode = "edgelengtharray"
            mesher.TargetEdgeLengthArrayName = "DistanceToCenterlines"
            mesher.TargetEdgeLengthFactor = 0.3
            mesher.MaxEdgeLength = 1.0
            mesher.Surface = disttocl.Surface
            mesher.Centerlines = disttocl.Centerlines
            mesher.Execute()
        else:
            raise ValueError("Invalid method")
        self.meshsurface = mesher.Surface
        self.mesh = mesher.Mesh
        self.view()

    def save(self, savepath):
        if not os.path.isdir(os.path.dirname(savepath)):
            os.makedirs(os.path.dirname(savepath))
        mwriter = vmtkscripts.vmtkMeshWriter()
        mwriter.OutputFileName = savepath
        mwriter.Mesh = self.mesh
        mwriter.Execute()

    def save_mesh_surface(self, savepath):
        if self.meshsurface == None:
            raise ValueError("Mesh surface empty, check that a mesh has been created.")
        if not os.path.isdir(os.path.dirname(savepath)):
            os.makedirs(os.path.dirname(savepath))
        sfwriter = vmtkscripts.vmtkSurfaceWriter()
        sfwriter.OutputFileName = savepath
        sfwriter.Surface = self.meshsurface


if __name__ == "__main__":
    pass
