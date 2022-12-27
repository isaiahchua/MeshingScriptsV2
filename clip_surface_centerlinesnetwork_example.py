import os
import numpy as np
from .MeshTools.centerlines import Centerlines
from .MeshTools.surface import Surface

wd = '../meshing/clipping_mesh/data/'
os.chdir(wd)
sffile = 'resurf/aorta.vtp'
clfile = 'centerlines/aorta.vtp'
clnetfile = 'centerlines/aorta_clnet2.vtp'
pklfile = 'centerlines/aorta.pkl'

clmodel = Centerlines()
clmodel.load(clpath=clnetfile, sfpath=sffile)
clmodel.extract_endpts(num_gs=1, num_eps=8)
clmodel.convert_to_array()

ptdata = clmodel.clarray['PointData']
print('=========== Point Data ===========')
for key in ptdata:
    if isinstance(ptdata[key], list):
        print('%s, %s' %(key, len(ptdata[key])))
    if isinstance(ptdata[key], np.ndarray):
        print('%s, %s' %(key, ptdata[key].shape))
    if isinstance(ptdata[key], type(ptdata)):
        print('%s, %s' %(key, ptdata[key].keys))

celldata = clmodel.clarray['CellData']
print('=========== Cell Data ===========')
for key in celldata:
    if isinstance(celldata[key], list):
        print('%s, %s' %(key, len(celldata[key])))
    if isinstance(celldata[key], np.ndarray):
        print('%s, %s' %(key, celldata[key].shape))
    if isinstance(celldata[key], type(ptdata)):
        print('%s, %s' %(key, celldata[key].keys))

celldata['GroupIds'] = np.array([0,1,2,3,4,2,2,2,5,6], dtype=np.int32)
clmodel.add_cell_labels()
clmodel.convert_to_cl()
sfmodel = Surface()
sfmodel.load(sfpath=sffile)
sfmodel.clip(cl=clmodel.centerlines, method="auto")
clmodel.surface = sfmodel.surface

for cell in celldata['CellPointIds']:
    print(cell)
print('GroupIds: %s' %(celldata['GroupIds']))
print('TractIds: %s' %(celldata['TractIds']))
print('CenterlineIds: %s' %(celldata['CenterlineIds']))
print('Blanking: %s' %(celldata['Blanking']))

print('Viewing CellPointIds...')
clmodel.view(celldata='CellLabels')
print('Viewing GroupIds...')
clmodel.view(celldata='GroupIds')
print('Viewing TractIds...')
clmodel.view(celldata='TractIds')
print('Viewing CenterlineIds...')
clmodel.view(celldata='CenterlineIds')
print('Viewing Blanking...')
clmodel.view(celldata='Blanking')
