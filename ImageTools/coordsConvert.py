# This is for the conversion between Patient Coordinates and Image Coordinates

def convertPatient2ImageCoords(pt, origin, spacing):
   rs = [0] * 3
   rs[0] = round((pt[0] - origin[0]) / spacing[0])
   rs[1] = round((pt[1] - origin[1]) / spacing[1])
   rs[2] = round((pt[2] - origin[2]) / spacing[2])

   return rs


def convertImage2PatientCoords(pt, origin, spacing):
   rs = [0] * 3
   rs[0] = round(pt[0] * spacing[0] + origin[0], 2)
   rs[1] = round(pt[1] * spacing[1] + origin[1], 2)
   rs[2] = round(pt[2] * spacing[2] + origin[2], 2)

   return rs