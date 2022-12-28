import sys, os, traceback
import vtk
import csv
from glob import glob
import argparse
from vmtk import vmtkscripts
from MeshTools import Centerlines, Surface, Mesh, Visualize
from utilities import FileManager

class Recorder():

    def __init__(self, savePath, headers=None):
        self.savePath = savePath
        self.headers = headers

        if not os.path.isdir(os.path.dirname(self.savePath)):
            os.makedirs(os.path.dirname(self.savePath))
        if not os.path.exists(self.savePath):
            if not self.headers:
                raise Exception("No headers provided for new file")
            with open(self.savePath, "w", newline="") as f:
                writer = csv.writer(f, dialect="excel", delimiter="\t")
                writer.writerow(self.headers)

    def write(self, row):
        with open(self.savePath, "a", newline="") as f:
            writer = csv.writer(f, dialect="excel", delimiter="\t")
            writer.writerow(row)

def CreateMesh(surfacePath, dataLogger=None):
    newRow = [surfacePath, "", "False", ""]
    basename = os.path.basename(surfacePath).split(".", 1)[0]
    baseDir = os.path.dirname(surfacePath)
    try:
        sfModel = Surface()
        sfModel.load(sfpath=surfacePath)
        sfModel.smooth()
        sfModel.save_surface(os.path.join(baseDir, "smooth", basename + ".vtp"))
        clModel = Centerlines()
        clModel.surface = sfModel.surface
        clModel.create_cl(method="pickpoints")
        clModel.save_centerlines(os.path.join(baseDir, "centerlines", basename + ".vtp"))
        sfModel.centerlines = clModel.centerlines
        sfModel.clip(method="auto")
        sfModel.save_surface(os.path.join(baseDir, "clip", basename + ".vtp"))
        sfModel.extend(method="cl")
        sfModel.save_surface(os.path.join(baseDir, "extend", basename +  ".vtp"))
        sfModel.resurf(method="cellarea")
        sfModel.save_surface(os.path.join(baseDir, "resurf", basename + ".vtp"))
        clModel.surface = sfModel.surface
        clModel.create_cl2()
        mshModel = Mesh()
        mshModel.surface = sfModel.surface
        mshModel.centerlines = clModel.centerlines
        mshModel.create_mesh(method="adaptive")
        mshModel.save(os.path.join(baseDir, "mesh", basename + ".vtu"))
        mshModel.save_mesh_surface(os.path.join(baseDir, "mesh", basename + ".vtp"))
        newRow[1] = os.path.join(baseDir, "mesh", basename + ".vtu")
        newRow[2] = "True"
        newRow[3] = "Done"
        if dataLogger:
            dataLogger.write(newRow)

    except:
        error = traceback.format_exc()
        print(error)
        if dataLogger:
            newRow[3] = error
            dataLogger.write(newRow)


def main(args):
    input_counter = 0
    recording = True
    if args.parent:
        input_counter += 1
        input_type = "parent"
    if args.paths:
        input_counter += 1
        input_type = "list"
    if args.filename:
        input_counter += 1
        input_type = "file"
    if input_counter == 0:
        raise Exception("No valid input provided")
    elif input_counter > 1:
        raise Exception("More than one type of inputs put")
    if args.log == None:
        recording = False
    if recording:
        headers = ["original", "final", "successful", "remarks"]
        dataLogger = Recorder(args.log, headers)

    if input_type == "parent":
        fileSorter = FileManager(args.parent, args.sub)
        fileSorter.makeFileList()
        fileList = fileSorter.getFiles()
    elif input_type == "list":
        fileList = args.paths
    elif input_type == "file":
        fileList = [args.filename]

    if recording:
        for file in fileList:
            CreateMesh(file, dataLogger)
    else:
        for file in fileList:
            CreateMesh(file)

class ProcessPath(argparse.Action):

    def __init__(self, option_strings, dest, **kwargs):
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string):
        if self.dest == "src":
            if (values == None) or (values == ".") or (values == "./"):
                values = os.getcwd()
            if values[-1] != "/":
                values += "/"
        elif self.dest == "sub":
            for i, dir in enumerate(values):
                if dir[-1] != "/":
                    values[i] += "/"
        setattr(namespace, self.dest, values)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=
                "Generate volumetric mesh for simulations from surface meshes.")
    parser.add_argument("-p", "--par-dir", metavar="DIR",
                        dest="parent", type=str, default=None, help=
                        ("Parent directory to begin recursive search for vtp files"))
    parser.add_argument("-l", "--list", metavar="PATHS", dest="paths",
                        default=None, help=
                        ("File paths to raw surface mesh to be processed"))
    parser.add_argument("-f", "--file", metavar="PATH", dest="filename",
                        default=None, help=
                        ("File name to mesh"))
    parser.add_argument("-s", "--sub-dir", metavar="DIR", nargs="*", dest="sub",
                        action=ProcessPath, default=None, help=
                        ("Basenames of the sub-directories to search for "
                         "surface files. Default: None"))
    parser.add_argument("-z", "--log-file", metavar="LOG", dest="log", type=str,
                        default=None, help=
                        ("File path for saving log file"))
    args = parser.parse_args()

    main(args)
