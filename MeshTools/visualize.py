import sys
from vmtk import vmtkscripts


class Visualize:
    def __init__(
        self, centerlines=None, surface=None, surface2=None, mesh=None, mesh2=None,
        cl_image=None, sf_image=None
    ):
        self.centerlines = centerlines
        self.surface = surface
        self.surface2 = surface2
        self.mesh = mesh
        self.mesh2 = mesh2
        self.climage = cl_image
        self.sfimage = sf_image
        self.renderer = vmtkscripts.vmtkRenderer()
        self.renderer.Initialize()

    def view_surface(self):
        self.renderer.Initialize()
        if self.surface == None:
            raise ValueError("Empty surface")
        elif self.surface2 != None:
            sfviewer = vmtkscripts.vmtkSurfaceViewer()
            sfviewer.vmtkRenderer = self.renderer
            sfviewer.Display = 0
            sfviewer.Opacity = 0.25
            sfviewer.Surface = self.surface2
            sfviewer2 = vmtkscripts.vmtkSurfaceViewer()
            sfviewer2.vmtkRenderer = self.renderer
            sfviewer2.Display = 1
            sfviewer2.Surface = self.surface
            sfviewer.Execute()
            sfviewer2.Execute()
        else:
            sfviewer = vmtkscripts.vmtkSurfaceViewer()
            sfviewer.vmtkRenderer = self.renderer
            sfviewer.Surface = self.surface
            sfviewer.Execute()
        self.renderer.Deallocate()

    def view_centerlines(self, ptarray="", cellarray=""):
        self.renderer.Initialize()
        if self.centerlines == None:
            raise ValueError("No centerlines")
        if self.surface != None:
            sfviewer = vmtkscripts.vmtkSurfaceViewer()
            sfviewer.Display = 0
            sfviewer.Opacity = 0.25
            sfviewer.vmtkRenderer = self.renderer
            sfviewer.Surface = self.surface
            sfviewer.Execute()
        clviewer = vmtkscripts.vmtkCenterlineViewer()
        clviewer.Centerlines = self.centerlines
        clviewer.vmtkRenderer = self.renderer
        clviewer.PointDataArrayName = ptarray
        clviewer.CellDataArrayName = cellarray
        clviewer.Execute()
        self.renderer.Deallocate()

    def view_mesh(self):
        self.renderer.Initialize()
        if self.mesh == None:
            raise ValueError("No mesh")
        elif self.mesh2 != None:
            mviewer = vmtkscripts.vmtkMeshViewer()
            mviewer.vmtkRenderer = self.renderer
            mviewer.Display = 0
            mviewer.Opacity = 0.25
            mviewer.Mesh = self.mesh2
            mviewer2 = vmtkscripts.vmtkMeshViewer()
            mviewer2.vmtkRenderer = self.renderer
            mviewer2.Display = 1
            mviewer2.Mesh = self.mesh
            mviewer.Execute()
            mviewer2.Execute()
        else:
            mviewer = vmtkscripts.vmtkMeshViewer()
            mviewer.vmtkRenderer = self.renderer
            mviewer.Mesh = self.mesh
            mviewer.Execute()
        self.renderer.Deallocate()

    def view_cl_image(self):
        if self.climage == None:
            raise ValueError("No centerlines image")
        climgviewer = vmtkscripts.vmtkImageViewer()
        climgviewer.vmtkRenderer = self.renderer
        climgviewer.Image = self.climage
        climgviewer.Execute()
        self.renderer.Deallocate()


if __name__ == "__main__":
    pass
