import SimpleITK as sitk
import numpy as np

def get_img(imgpath):
    reader = sitk.ImageFileReader()
    reader.SetFileName(imgpath)
    img = reader.Execute()

    origin = img.GetOrigin()
    spacing = img.GetSpacing()
    imgarray = sitk.GetArrayFromImage(img)

    return origin, spacing, imgarray

if __name__ == '__main__':
    filepath = '/home/biomind/ffr/head_vessel/output/abnormal/20181009000123/label_cut.nii.gz'
    ref, spac, imgarr = get_img(filepath)
    print(f'original image shape: {imgarr.shape}')
    print(f'original image unique values: {np.unique(imgarr)}')
    print(f'original image origin: {ref}')
    print(f'original image spacing: {spac}')
    
    filepath = ('/home/biomind/ffr/centerlines_model/unedited_data/abnormal/'
                'vessels_pixel/20181009000123_1.nii.gz'
               )
    ref, spac, imgarr = get_img(filepath)
    print(f'original image shape: {imgarr.shape}')
    print(f'original image unique values: {np.unique(imgarr)}')
    print(f'original image origin: {ref}')
    print(f'original image spacing: {spac}')

    filepath = ('/home/biomind/ffr/centerlines_model/unedited_data/abnormal/'
                'vessels_pixel/20181009000123_2.nii.gz'
               )
    ref, spac, imgarr = get_img(filepath)
    print(f'original image shape: {imgarr.shape}')
    print(f'original image unique values: {np.unique(imgarr)}')
    print(f'original image origin: {ref}')
    print(f'original image spacing: {spac}')

    filepath = ('/home/biomind/ffr/centerlines_model/unedited_data/abnormal/'
                'vessels_pixel/20181009000123_3.nii.gz'
               )
    ref, spac, imgarr = get_img(filepath)
    print(f'original image shape: {imgarr.shape}')
    print(f'original image unique values: {np.unique(imgarr)}')
    print(f'original image origin: {ref}')
    print(f'original image spacing: {spac}')
