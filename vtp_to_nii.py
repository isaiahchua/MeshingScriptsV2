import itk
from MeshTools import Surface

sfPath = "/Users/biomind/OneDrive - Hanalytics Pte Ltd/datasets/ffr_demo/20180703001516/resurf/output_vessel_1.vtp"
imgPath = "/Users/biomind/OneDrive - Hanalytics Pte Ltd/datasets/ffr_demo/images/20180703001516/Segmentation-cxm-label-2.nii.gz"
img = itk.imread(imgPath)
dimensions = list(itk.size(img))
sfFilter = Surface()
sfFilter.load(sfPath)
sfFilter.set_image_dimensions(dimensions)
sfFilter.convert_to_image()

