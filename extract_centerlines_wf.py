import sys, os, traceback
import glob
import csv
import pickle
import argparse
from MeshTools import *
from utilities import FileManager

class WriteVesselIssues:

    def __init__(self):
        self.patientName = None
        self.filePath = None
        self.vesselName = None
        self.savePath = None

    def setSaveDirectory(self, savePath):
        self.savePath = savePath

    def setPath(self, filePath):
        self.filePath = filePath

    def setPatient(self, patientName):
        self.patientName = patientName

    def setVessel(self, vesselName):
        self.vesselName = vesselName

    def writeLine(self, statement):
        with open(self.savePath, "a", newline="") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerow([self.filePath, self.patientName,
                             self.vesselName, statement])

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

def Workflow(fileManager, issueLog, saveList=False, verbose=False, continuous=False, noWindow=False):
    for _ in range(fileManager.getListSize()):
        surfacePath = fileManager.getFile()
        issueLog.setPath(surfacePath)
        patientName = surfacePath.split("/")[-3]
        issueLog.setPatient(patientName)
        basePath = surfacePath.split(".")[0]
        vesselName = os.path.basename(basePath)
        issueLog.setVessel(vesselName)
        fileManager.insertFileAtStartOn()
        reappendFile = True
        print("\n-----------------------------------------------------------------------\n")
        print(f"Creating centerlines from : {surfacePath}\n")
        try:
            centerlineFilter = Centerlines()
            centerlineFilter.load(sfpath=surfacePath)
            centerlineFilter.create_cl2()
            if not noWindow:
                centerlineFilter.view()
            if continuous:
                answer = "y"
            else:
                while True:
                    print("\nOK? (Y/N)")
                    answer = input()
                    if answer in "yYnN":
                        break
                    else:
                        print("Invalid input.")

            if answer.lower() == "y":
                reappendFile = False
                centerlineFilter.convert_to_array()
                centerlineFilter.save_centerlines(basePath + "_cl.vtp")
                centerlineFilter.save_points(basePath + "_cl.npy")
                centerlineFilter.save_dict(basePath + "_cl.pkl")
                issueLog.writeLine("Successful")
            else:
                if verbose:
                    print("What is the issue?")
                    answer2 = input()
                else:
                    answer2 = "Unsuccessful"
                issueLog.writeLine(answer2)

        except Exception as e:
            print(traceback.format_exc())
            issueLog.writeLine(e)
            pass

        if continuous:
            fileManager.insertFileAtStartOff()
            if saveList:
                if reappendFile:
                    fileManager.addFile(surfacePath)
                if fileManager.fileList:
                    fileManager.savePatientList()
                else:
                    fileManager.deletePatientList()
            continue
        else:
            while True:
                print("\nContinue? (Y/N)")
                answer3 = input()
                if answer3 in "yYnN":
                    break
                else:
                    print("Invalid input.")
            if answer3.lower() == "y":
                fileManager.insertFileAtStartOff()
            if saveList:
                if reappendFile:
                    fileManager.addFile(surfacePath)
                if fileManager.fileList:
                    fileManager.savePatientList()
                else:
                    fileManager.deletePatientList()
            if answer3.lower() == "y":
                continue
            else:
                break

def CreateCenterlines(parentDirectory, logPath, surfaceListPath="",
                      subDirectory=None, verbose=False, continuous=False, noWindow=False):
    dataLogger = WriteVesselIssues()
    dataLogger.setSaveDirectory(logPath)
    fileSorter = FileManager(parentDirectory, subDirectory)
    if not surfaceListPath:
        fileSorter.makeFileList()
        savePatientList = False
    else:
        fileSorter.setPatientListPath(surfaceListPath)
        savePatientList = True
        if os.path.exists(surfaceListPath):
            fileSorter.loadPatientList()
        else:
            fileSorter.makeFileList()
            fileSorter.savePatientList()
    Workflow(fileSorter, dataLogger, savePatientList, verbose, continuous, noWindow)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=
            "Create centerlines for successfully meshed vessels.")
    parser.add_argument("src", metavar="SRC", type=str, default=None, action=ProcessPath,
                        help="The parent directory where the surfaces are stored.")
    parser.add_argument("-l","--log", metavar="PATH", type=str, default=None,
                        help=("Where to save the log file "
                              "during runtime. Default: <SRC>/log.csv"))
    parser.add_argument("-r", "--retrieve-patients", metavar="PATH",
                        dest="pat", type=str, nargs="?", default="",
                        help=("Retrieve list of remaining patients from PATH, "
                              "also specifies save location for the list."
                              "Default: <SRC>/patient_paths.pkl"))
    parser.add_argument("-s", "--sub-dir", metavar="DIRNAME", nargs="*", dest="sub",
                        action=ProcessPath, default=None,
                        help=("Basenames of the sub-directories to search for "
                              "surface files. Default: None"))
    parser.add_argument("-v", "--verbose", action="store_true",
                        help=("Enable logging comments after centerline generation. "
                              "If disabled only whether centerline generation was "
                              "successful and errors will be stored into log file."))
    parser.add_argument("-c", "--continuous", action="store_true",
                        help=("Disable choice to exit after centerline generation. "))
    parser.add_argument("-w", "--no-window", dest="noWindow", action="store_true",
                        help=("Do not render the finished task in a window. "))
    args = parser.parse_args()
    if args.log == None:
        args.log = args.src + "log.csv"
    if args.pat == None:
        args.pat = args.src + "patient_paths.pkl"

    print(f"\nParent Directory : {args.src}")
    print(f"Log File Directory : {args.log}")
    if not args.pat == "":
        print(f"Patient List Directory : {args.pat}")
    print(f"Subdirectories : {args.sub}")

    CreateCenterlines(args.src, args.log, args.pat, args.sub, args.verbose, args.continuous, args.noWindow)
