import sys
import numpy as np
import itk
import cc3d

filename = sys.argv[1]
image = itk.imread(filename)
arr = itk.GetArrayFromImage(image)
mask = np.nonzero(arr)
arr = np.ones(arr.shape, dtype=bool)
arr[mask] = 0
labels, N = cc3d.connected_components(arr, connectivity=6, return_N=True)
print(N)
