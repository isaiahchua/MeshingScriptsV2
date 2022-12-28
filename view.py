import argparse
from vmtk import vmtkscripts
from MeshTools import Visualize

def ReadForCenterlines(filepaths):
    files = []
    reader = vmtkscripts.vmtkSurfaceReader()
    reader.InputFileName = filepaths[0]
    reader.Execute()
    files.append(reader.Surface)
    if len(filepaths) == 2:
        reader2 = vmtkscripts.vmtkSurfaceReader()
        reader2.InputFileName = filepaths[1]
        reader2.Execute()
        files.append(reader2.Surface)
    else:
        files.append(None)
    return files

def ReadForSurface(filepaths):
    return ReadForCenterlines(filepaths)

def ReadForMesh(filepaths):
    files = []
    reader = vmtkscripts.vmtkMeshReader()
    reader.InputFileName = filepaths[0]
    reader.Execute()
    files.append(reader.Mesh)
    if len(filepaths) == 2:
        reader2 = vmtkscripts.vmtkMeshReader()
        reader2.InputFileName = filepaths[1]
        reader2.Execute()
        files.append(reader2.Mesh)
    else:
        files.append(None)
    return files

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=
                "Wrapper for visualizing surface, centerlines and mesh with vmtk")
    parser.add_argument("-c", "--centerline", action="store_true",
                        help=("View centerline mode"))
    parser.add_argument("-s", "--surface", action="store_true",
                        help=("View surface mode"))
    parser.add_argument("-m", "--mesh", action="store_true",
                        help=("View mesh mode"))
    parser.add_argument("paths", metavar="PATH(S)", type=str, nargs="*",
                        help=("Insert paths (max 2) to files to open in correct order:\n"
                              "centerlines, surface, surface2, mesh, mesh2"))
    parser.add_argument("options", nargs="?", default="",
                        help=("Additional options for viewer,"
                              "must be presented in correct order"))
    args = parser.parse_args()

    no_of_trues = args.centerline + args.surface + args.mesh
    if no_of_trues != 1:
        raise Exception("Only one viewing mode allowed at once")
    if len(args.paths) > 2:
        raise Exception("A maximum of two paths are allowed")

    if args.centerline:
        files = ReadForCenterlines(args.paths)
        print(files)
        viewer = Visualize(centerlines=files[0], surface=files[1])
        if args.options:
            viewer.view_centerlines(*args.options)
        else:
            viewer.view_centerlines()
    if args.surface:
        files = ReadForSurface(args.paths)
        viewer = Visualize(surface=files[0], surface2=files[1])
        viewer.view_surface()
    if args.mesh:
        files = ReadForMesh(args.paths)
        viewer = Visualize(mesh=files[0], mesh2=files[1])
        viewer.view_mesh()
