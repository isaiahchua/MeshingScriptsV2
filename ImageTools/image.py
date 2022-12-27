import os
import numpy as np
import SimpleITK as sitk
from .coordsConvert import convertPatient2ImageCoords


class Image:
    def __init__(self):
        self.image = None
        self.imgarray = None
        self.clpts = None
        self.origin = (0., 0., 0.)
        self.spacing = (0., 0., 0.)
        self.basename = ""

    def load(self, imgpath=None, clpath=None):
        if imgpath == None:
            raise ValueError("No file provided")
        imgreader = sitk.ImageFileReader()
        imgreader.SetFileName(imgpath)
        self.image = imgreader.Execute()
        self.origin = self.image.GetOrigin()
        self.spacing = self.image.GetSpacing()
        self.basename = os.path.basename(imgpath).split(".")[0]

        if clpath != None:
            self.clpts = np.load(clpath)

    def convert_to_array(self):
        if self.image == None:
            raise ValueError("No image loaded")
        self.imgarray = sitk.GetArrayFromImage(self.image)

    def convert_to_imagepts(self, dimensions=[64, 64, 64], origin=[0, 0, 0], spacing=[1, 1, 1]):
        if isinstance(self.clpts, type(None)):
            raise ValueError(
                "use convert_to_array method create an ArrayDict from the loaded centerlines."
            )
        self.imgarray = np.zeros(dimensions)
        testarray = []
        for pt in self.clpts:
            img_pt = convertPatient2ImageCoords(pt[::-1], origin, spacing)
            testarray.append(img_pt)
            # self.imgarray[img_pt] = 1
        return np.array(testarray)

    def convert_to_image(self):
        if isinstance(self.imgarray, type(None)):
            raise ValueError(
                "use convert_to_imagepts method create an image mask from the loaded centerlines array."
            )
        self.image = sitk.GetImageFromArray(self.imgarray)

    def save_image(self, savepath):
        if self.image == None:
            raise ValueError("no centerline image.")
        sitk.WriteImage(self.image, savepath)

    def save_imagepts(self, savepath):
        if self.clpts == None:
            raise ValueError("no centerline points")
        np.save(savepath, self.clpts)

    def save_labels(self, savedir, basename=None):
        if isinstance(self.imgarray, type(None)):
            raise ValueError(
                "No image array, use convert_to_array to convert a loaded image into a numpy array"
            )
        if basename == None:
            basename = self.basename
        min_value = self.imgarray.min()
        max_value = self.imgarray.max()
        for i in range(min_value, max_value + 1):
            if i <= 0:
                continue
            output_array = np.zeros_like(self.imgarray)
            output_array[self.imgarray == i] = 1
            output_image = sitk.GetImageFromArray(output_array)
            output_image.SetOrigin(self.origin)
            output_image.SetSpacing(self.spacing)
            filename = basename + "_" + str(i) + ".nii.gz"
            if savedir[-1] == "/":
                filepath = savedir + filename      
            else:
                filepath = savedir + "/" + filename
            sitk.WriteImage(output_image, filepath)
            print(f'Label {str(i)} --> {filename}')

if __name__ == "__main__":
    pass
