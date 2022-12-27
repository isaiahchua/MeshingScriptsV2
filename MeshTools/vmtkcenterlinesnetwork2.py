#!/usr/bin/env python
# -*- coding: utf-8 -*-

## Program:   VMTK
## Module:    $RCSfile: vmtkcenterlinesnetwork.py,v $
## Language:  Python
## Date:      $Date: 2018/04/24 09:52:56 $
## Version:   $Revision: 1.20 $

##   Copyright (c) Richard Izzo, Luca Antiga. All rights reserved.
##   See LICENCE file for details.

##      This software is distributed WITHOUT ANY WARRANTY; without even
##      the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
##      PURPOSE.  See the above copyright notices for more information.


from __future__ import absolute_import #NEEDS TO STAY AS TOP LEVEL MODULE FOR Py2-3 COMPATIBILITY
import vtk
import sys

from vmtk import vtkvmtk
from vmtk import pypes
from vmtk import vmtkcenterlines, vmtkcenterlinestonumpy, vmtknetworkextraction, vmtkdelaunayvoronoi, vmtknumpytocenterlines, vmtksurfacecapper
from joblib import Parallel, delayed
import random
import numpy as np


def _compute_centerlines_network(surfaceAddress, delaunayAddress, voronoiAddress, poleIdsAddress, cell, points):
    '''a method to compute centerlines which can be called in parallel
    
    Arguments:
        surfaceAddress (str): the input memory address of the surface to calculate centerlines of
        delaunayAddress (str): the memory address of a previously computed delaunay triangulation of the 
            surface vtkUnstructuredGrid 
        voronoiAddress (str): the memory address of the previously computed voronoi diagram vtkPolyData
        poleIdsAddress (str): the memory address of the previously computed poleIds vtkIdList
        cell (np.array): the cellID connectivity list
        points (np.array): the x,y,z coordinates of points identified in the cell argument
    '''

    surface = vtk.vtkPolyData(surfaceAddress)
    delaunay = vtk.vtkUnstructuredGrid(delaunayAddress)
    voronoi = vtk.vtkPolyData(voronoiAddress)
    poleIds = vtk.vtkIdList(poleIdsAddress)

    cl = _compute_centerline_branch(surface, delaunay, voronoi, poleIds, cell, points)

    clConvert = vmtkcenterlinestonumpy.vmtkCenterlinesToNumpy()
    clConvert.Centerlines = cl
    clConvert.LogOn = 0
    clConvert.Execute()
    return clConvert.ArrayDict

def _compute_centerline_branch(surface, delaunay, voronoi, poleIds, cell, points):
    cellStartIdx = cell[0]
    cellEndIdx = cell[-1]
    cellStartPoint = points[cellStartIdx].tolist()
    cellEndPoint = points[cellEndIdx].tolist()
    cl = vmtkcenterlines.vmtkCenterlines()
    cl.Surface = surface
    cl.DelaunayTessellation = delaunay
    cl.VoronoiDiagram = voronoi
    cl.PoleIds = poleIds
    cl.SeedSelectorName = 'pointlist'
    # since we only set one target seed at a time, setting StopFastMarchingOnReachingTarget
    # greatly speeds up algorithm execution time.
    cl.StopFastMarchingOnReachingTarget = 1
    cl.SourcePoints = cellStartPoint
    cl.TargetPoints = cellEndPoint
    cl.AppendEndPoints = 0
    cl.LogOn = 0
    cl.Execute()
    return cl.Centerlines

def _append_open_ends(centerlines, cellIds, pointIds, points, radiusArrayName):
    print("Appending End Points...")
    completeCenterlines = vtk.vtkPolyData()
    completeCenterlineCellArray = vtk.vtkCellArray()
    completeCell = vtk.vtkIdList()
    completeCenterlinesPoints = vtk.vtkPoints()
    completeCenterlineRadiusArray = vtk.vtkDoubleArray()

    centerlineRadiusArray = centerlines.GetPointData().GetArray(radiusArrayName)
    completeCenterlinesPoints.DeepCopy(centerlines.GetPoints())
    completeCenterlineRadiusArray.DeepCopy(centerlineRadiusArray)
    completeCenterlineRadiusArray.SetName(radiusArrayName)

    noOfCells = centerlines.GetNumberOfCells()
    counter = 0
    for i in range(noOfCells):
        cell = centerlines.GetCell(i)
        if cellIds[counter] == i:
            endPointId = completeCenterlinesPoints.InsertNextPoint(points[counter])
            completeCell.Initialize()
            noCellPoints = cell.GetNumberOfPoints()
            completeCell.SetNumberOfIds(noCellPoints + 1)
            if pointIds[counter] == 0:
                completeCell.SetId(0, endPointId)
                for k in range(noCellPoints):
                    completeCell.SetId(k+1, cell.GetPointId(k))
                completeCenterlineRadiusArray.InsertNextValue(
                            centerlineRadiusArray.GetValue(cell.GetPointId(0)))
            else:
                completeCell.SetId(noCellPoints, endPointId)
                for k in range(noCellPoints):
                    completeCell.SetId(k, cell.GetPointId(k))
                completeCenterlineRadiusArray.InsertNextValue(
                            centerlineRadiusArray.GetValue(cell.GetPointId(noCellPoints - 1)))
            if counter < len(cellIds) - 1:
                counter += 1
        else:
            completeCell.DeepCopy(cell.GetPointIds())
        completeCenterlineCellArray.InsertNextCell(completeCell)

    completeCenterlines.SetPoints(completeCenterlinesPoints)
    completeCenterlines.SetLines(completeCenterlineCellArray)
    completeCenterlines.GetPointData().AddArray(completeCenterlineRadiusArray)

    return completeCenterlines

class vmtkCenterlinesNetwork2(pypes.pypeScript):

    def __init__(self):

        pypes.pypeScript.__init__(self)

        self.Surface = None
        self.Centerlines = None
        self.RadiusArrayName = 'MaximumInscribedSphereRadius'
        self.BlankingArrayName = "Blanking"
        self.GroupIdsArrayName = "GroupIds"
        self.CenterlineIdsArrayName = "CenterlineIds"
        self.TractIdsArrayName = "TractIds"
        self.CostFunction = '1/R'

        self.EikonalSolutionArrayName = 'EikonalSolution'
        self.EdgeArrayName = 'EdgeArray'
        self.EdgePCoordArrayName = 'EdgePCoordArray'
        self.CostFunctionArrayName = 'CostFunctionArray'

        self.DelaunayTessellation = None
        self.VoronoiDiagram = None
        self.PoleIds = None
        self.RandomSeed = None
        
        self.AppendOpenEnds = 1
        
        # When using Joblib Under Windows, it is important to protect the main loop of code to avoid recursive spawning
        # of subprocesses. Since we cannot guarantee no code will run outside of “if __name__ == ‘__main__’” blocks
        # (only imports and definitions), we don't use joblib on windows.
        # Isaiah: Added Mac as well (Darwin) 
        if (sys.platform == 'win32') or (sys.platform == 'win64') or (sys.platform == 'cygwin') or (sys.platform == 'darwin'):
            self.PrintLog('Centerlines extraction on windows computer will execute serially.')
            self.PrintLog('To speed up execution, please run vmtk on unix-like operating system and enable joblib')
            self.UseJoblib = False
        else:
            self.UseJoblib = True
        
        self.vmtkRenderer = None
        self.OwnRenderer = 0

        self.SetScriptName('vmtkcenterlinesnetwork2')
        self.SetScriptDoc('compute centerlines from a branching tubular surface automatically.')
        self.SetInputMembers([
            ['Surface','i','vtkPolyData',1,'','the input surface','vmtksurfacereader'],
            ['vmtkRenderer','renderer','vmtkRenderer',1,'','external renderer']])
        self.SetOutputMembers([
            ['Centerlines','o','vtkPolyData',1,'','the output centerlines','vmtksurfacewriter'],
            ['RadiusArrayName','radiusarray','str',1,'','name of the array where radius values of maximal inscribed spheres are stored'],
            ['EikonalSolutionArrayName','eikonalsolutionarray','str',1],
            ['EdgeArrayName','edgearray','str',1],
            ['EdgePCoordArrayName','edgepcoordarray','str',1],
            ['CostFunction','costfunction','str',1,'','cost function minimized during centerline computation'],
            ['CostFunctionArrayName','costfunctionarray','str',1],
            ['DelaunayTessellation','delaunaytessellation','vtkUnstructuredGrid',1,'','','vmtkmeshwriter'],
            ['VoronoiDiagram','voronoidiagram','vtkPolyData',1,'','','vmtksurfacewriter'],
            ['PoleIds','poleids','vtkIdList',1],
            ['RandomSeed','randomseed','int',1],
            ['UseJoblib','usejoblib','bool',1]])

    def Execute(self):
        if self.Surface == None:
            self.PrintError('Error: No input surface.')

        # feature edges are used to find any holes in the surface.
        # fedges = vtk.vtkFeatureEdges()
        # fedges.BoundaryEdgesOn()
        # fedges.FeatureEdgesOff()
        # fedges.ManifoldEdgesOff()
        # fedges.SetInputData(self.Surface)
        # fedges.Update()
        # ofedges = fedges.GetOutput()

        # if numEdges is not 0, then there are holes which need to be capped
        # numEdges = ofedges.GetNumberOfPoints()
        # if numEdges != 0:
            # tempcapper = vmtksurfacecapper.vmtkSurfaceCapper()
            # tempcapper.Surface = self.Surface
            # tempcapper.Interactive = 0
            # tempcapper.Execute()

            # networkSurface = tempcapper.Surface
        # else:
            # networkSurface = self.Surface

        # randomly select one cell to delete so that there is an opening for
        # vmtkNetworkExtraction to use.
        # numCells = networkSurface.GetNumberOfCells()
        # random_generator = random.Random()
        # if self.RandomSeed is not None:
            # random_generator.seed(self.RandomSeed)
        # cellToDelete = random_generator.randrange(0, numCells-1)
        # networkSurface.BuildLinks()
        # networkSurface.DeleteCell(cellToDelete)
        # networkSurface.RemoveDeletedCells()

        surfaceCapper = vtkvmtk.vtkvmtkCapPolyData()
        surfaceCapper.SetInputData(self.Surface)
        surfaceCapper.SetDisplacement(0.0)
        surfaceCapper.SetInPlaneDisplacement(0.0)
        surfaceCapper.Update()
        centerlineInputSurface = surfaceCapper.GetOutput()
        capCenterIds = surfaceCapper.GetCapCenterIds()

        if self.AppendOpenEnds:
            capPoints = []
            for i in range(capCenterIds.GetNumberOfIds()):
                capId = capCenterIds.GetId(i)
                capPt = [0, 0, 0]
                centerlineInputSurface.GetPoint(capId, capPt)
                capPoints.append(capPt)

        # extract the network of approximated centerlines
        net = vmtknetworkextraction.vmtkNetworkExtraction()
        net.Surface = self.Surface
        net.AdvancementRatio = 1.05
        net.Execute()
        network = net.Network

        convert = vmtkcenterlinestonumpy.vmtkCenterlinesToNumpy()
        convert.Centerlines = network
        convert.LogOn = False
        convert.Execute()
        ad = convert.ArrayDict
        cellDataTopology = ad['CellData']['Topology']

        # the network topology identifies an the input segment with the "0" id.
        # since we artificially created this segment, we don't want to use the
        # ends of the segment as source/target points of the centerline calculation
        # nodeIndexToIgnore = np.where(cellDataTopology[:,0] == 0)[0][0]
        # keepCellConnectivityList = []
        # pointIdxToKeep = np.array([])
        # removeCellLength = 0
        # we remove the cell, points, and point data which are associated with the
        # segment we want to ignore
        # for loopIdx, cellConnectivityList in enumerate(ad['CellData']['CellPointIds']):
            # if loopIdx == nodeIndexToIgnore:
                # removeCellStartIdx = cellConnectivityList[0]
                # removeCellEndIdx = cellConnectivityList[-1]
                # removeCellLength = cellConnectivityList.size
                # if (removeCellEndIdx + 1) - removeCellStartIdx != removeCellLength:
                    # raise(ValueError)
                # continue
            # else:
                # rescaledCellConnectivity = np.subtract(cellConnectivityList, removeCellLength, where=cellConnectivityList >= removeCellLength)
                # keepCellConnectivityList.append(rescaledCellConnectivity)
                # pointIdxToKeep = np.concatenate((pointIdxToKeep, cellConnectivityList)).astype(int)
        keepCellConnectivityList = ad['CellData']['CellPointIds']
        newPoints = ad['Points']  # [pointIdxToKeep]
        newRadius = ad['PointData'] # ['Radius'][pointIdxToKeep]
        if self.AppendOpenEnds:
            appendCellIds = []
            appendPointIds = []
            appendPoints = []
            for i, cell in enumerate(keepCellConnectivityList):
                startPtId = cell[0]
                endPtId = cell[-1]
                startPt = newPoints[startPtId]
                endPt = newPoints[endPtId]
                for capPt in capPoints:
                    dist1 = np.linalg.norm(startPt-capPt)
                    dist2 = np.linalg.norm(endPt-capPt)
                    if dist1 < 1e-5:
                        appendCellIds.append(i)
                        appendPointIds.append(0)
                        appendPoints.append(startPt)
                        break
                    if dist2 < 1e-5:
                        appendCellIds.append(i)
                        appendPointIds.append(1)
                        appendPoints.append(endPt)
                        break

        # precompute the delaunay tessellation for the whole surface.
        tessalation = vmtkdelaunayvoronoi.vmtkDelaunayVoronoi()
        tessalation.Surface = centerlineInputSurface
        tessalation.Execute()
        self.DelaunayTessellation = tessalation.DelaunayTessellation
        self.VoronoiDiagram = tessalation.VoronoiDiagram
        self.PoleIds = tessalation.PoleIds


        out = []
        self.PrintLog('Computing Centerlines ...')
        if self.UseJoblib:
            # vtk objects cannot be serialized in python. Instead of converting the inputs to numpy arrays and having
            # to reconstruct the vtk object each time the loop executes (a slow process), we can just pass in the
            # memory address of the data objects as a string, and use the vtk python bindings to create a python name
            # referring to the data residing at that memory address. This works because joblib executes each loop
            # iteration in a fork of the original process, providing access to the original memory space.
            # However, the process does not work for return arguments, since the original process will not have access to
            # the memory space of the fork. To return results we use the vmtkCenterlinesToNumpy converter.
            networkSurfaceMemoryAddress = centerlineInputSurface.__this__
            delaunayMemoryAddress = tessalation.DelaunayTessellation.__this__
            voronoiMemoryAddress = tessalation.VoronoiDiagram.__this__
            poleIdsMemoryAddress = tessalation.PoleIds.__this__
            numParallelJobs = -1
            
            
            # note about the verbose function: while Joblib can print a progress bar output (set verbose = 20),
            # it does not implement a callback function as of version 0.11, so we cannot report progress to the user
            # if we are redirecting standard out with the self.PrintLog method.
            outlist = Parallel(n_jobs=numParallelJobs, backend='multiprocessing', verbose=0)(
                delayed(_compute_centerlines_network)(networkSurfaceMemoryAddress,
                                              delaunayMemoryAddress,
                                              voronoiMemoryAddress,
                                              poleIdsMemoryAddress,
                                              cell,
                                              newPoints) for cell in keepCellConnectivityList)
            for item in outlist:
                npConvert = vmtknumpytocenterlines.vmtkNumpyToCenterlines()
                npConvert.ArrayDict = item
                npConvert.LogOn = 0
                npConvert.Execute()
                out.append(npConvert.Centerlines)
        else:
            for cell in keepCellConnectivityList:
                    cl = _compute_centerline_branch(centerlineInputSurface, tessalation.DelaunayTessellation, tessalation.VoronoiDiagram,
                                                    tessalation.PoleIds, cell, newPoints)
                    out.append(cl)

        # Append each segment's polydata into a single polydata object
        centerlineAppender = vtk.vtkAppendPolyData()
        for data in out:
            centerlineAppender.AddInputData(data)
        centerlineAppender.Update()
        if self.AppendOpenEnds:
            outputCenterlines = _append_open_ends(
                        centerlineAppender.GetOutput(), appendCellIds, appendPointIds,
                        appendPoints, self.RadiusArrayName)
        else:
            outputCenterlines = centerlineAppender.GetOutput()

        # branchExtractor = vtkvmtk.vtkvmtkCenterlineBranchExtractor()
        # branchExtractor.SetInputData(outputCenterlines)
        # branchExtractor.SetBlankingArrayName(self.BlankingArrayName)
        # branchExtractor.SetRadiusArrayName(self.RadiusArrayName)
        # branchExtractor.SetGroupIdsArrayName(self.GroupIdsArrayName)
        # branchExtractor.SetCenterlineIdsArrayName(self.CenterlineIdsArrayName)
        # branchExtractor.SetTractIdsArrayName(self.TractIdsArrayName)
        # branchExtractor.Update()

        # mergeCenterlines = vtkvmtk.vtkvmtkMergeCenterlines()
        # mergeCenterlines.SetInputConnection(centerlineAppender.GetOutputPort())
        # mergeCenterlines.SetRadiusArrayName(self.RadiusArrayName)
        # mergeCenterlines.SetGroupIdsArrayName(self.GroupIdsArrayName)
        # mergeCenterlines.SetCenterlineIdsArrayName(self.CenterlineIdsArrayName)
        # mergeCenterlines.SetTractIdsArrayName(self.TractIdsArrayName)
        # mergeCenterlines.SetBlankingArrayName(self.BlankingArrayName)
        # mergeCenterlines.SetResamplingStepLength(curveSamplingDistance)
        # mergeCenterlines.SetMergeBlanked(True)
        # mergeCenterlines.Update()

        # clean and strip the output centerlines so that redundant points are merged and tracts are combined
        centerlineCleaner = vtk.vtkCleanPolyData()
        centerlineCleaner.SetInputData(outputCenterlines)
        centerlineCleaner.PointMergingOff()
        centerlineCleaner.Update()

        centerlineStripper = vtk.vtkStripper()
        centerlineStripper.SetInputData(centerlineCleaner.GetOutput())
        centerlineStripper.JoinContiguousSegmentsOn()
        centerlineStripper.Update()

        self.Centerlines = centerlineStripper.GetOutput()


if __name__=='__main__':
    main = pypes.pypeMain()
    main.Arguments = sys.argv
    main.Execute()
