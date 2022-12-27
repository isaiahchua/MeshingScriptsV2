import os
import glob
import pickle

class FileManager:

    def __init__(self, parentDir, subDirs=None):
        self.parentDirectory = parentDir
        self.subDirectories = subDirs
        self.patientVessels = set()
        self.fileList = []
        self.tempFileList = []
        self.insertFileAtStart = False

    def __repr__(self):
        return str(self.fileList)

    def makeFileList(self):
        if self.subDirectories == None:
            self.fileList.extend([f for f in glob.glob(
                                    self.parentDirectory + f"**/*.vtp",
                                    recursive=True) if self.isSurface(f)])
            self.fileList.extend([f for f in glob.glob(
                                    self.parentDirectory + f"**/*.stl",
                                    recursive=True) if self.isSurface(f)])
        elif len(self.subDirectories) == 1:
            self.fileList = [f for f in glob.glob(
                    self.parentDirectory + f"**/{self.subDirectories[0]}*.vtp",
                    recursive=True) if self.isSurface(f)]
            self.fileList = [f for f in glob.glob(
                    self.parentDirectory + f"**/{self.subDirectories[0]}*.stl",
                    recursive=True) if self.isSurface(f)]
        else:
            for subDir in self.subDirectories:
                self.fileList.extend([f for f in glob.glob(
                                    self.parentDirectory + f"**/{subDir}*.vtp",
                                    recursive=True) if self.isSurface(f)
                                        and not self.isPatientVesselPresent(f)])
                self.fileList.extend([f for f in glob.glob(
                                    self.parentDirectory + f"**/{subDir}*.stl",
                                    recursive=True) if self.isSurface(f)
                                        and not self.isPatientVesselPresent(f)])

    def isSurface(self, filename):
        baseName = os.path.splitext(os.path.basename(filename))[0]
        if ("cl" in baseName) or ("net" in baseName):
            return False
        else:
            return True

    def isPatient(self, patient):
        return len(patient) == 14 and patient.isnumeric()

    def isPatientVesselPresent(self, file):
        vesselName = file.split("/")[-1]
        patientName = file.split("/")[-3]
        if patientName + vesselName in self.patientVessels:
            return True
        else:
            if self.isPatient(patientName):
                self.patientVessels.add(patientName + vesselName)

    def insertFileAtStartOn(self):
        self.insertFileAtStart = True

    def insertFileAtStartOff(self):
        self.insertFileAtStart = False

    def setPatientListPath(self, listPath):
        self.patientListPath = listPath

    def savePatientList(self):
        with open(self.patientListPath, "wb") as f:
            pickle.dump(self.fileList, f)

    def loadPatientList(self):
        with open(self.patientListPath, "rb") as f:
            self.fileList = pickle.load(f)
        if not self.fileList:
            raise Exception("Empty surface list file.")

    def deletePatientList(self):
        if os.path.exists(self.patientListPath):
            os.remove(self.patientListPath)
        else:
            print("Patient list file does not exist.")

    def getFile(self):
        return self.fileList.pop(0)

    def addFile(self, file):
        if self.insertFileAtStart:
            self.fileList.insert(0, file)
        else:
            self.fileList.append(file)

    def getFiles(self):
        return self.fileList

    def getListSize(self):
        return len(self.fileList)

if __name__ == "__main__":
    pass
