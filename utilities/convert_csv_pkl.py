import sys, os
import pickle
import csv

filename = sys.argv[1]
basename = os.path.splitext(filename)[0]

with open(filename, "r", newline="") as f:
    reader = csv.reader(f)
    patient_list = [str(item[0]) for item in reader]

with open(basename + ".pkl", "wb") as g:
    pickle.dump(patient_list, g)
