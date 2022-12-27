import os
import pickle
import csv
import argparse

def writeFirstPathToCSV(pklPath, csvPath):
    with open(pklPath, "rb") as src:
        inputList = pickle.load(src)
    item = inputList.pop(0)
    with open(csvPath, "a", newline="") as dest:
        writer = csv.writer(dest, delimiter="\t")
        writer.writerow([item])
    with open(pklPath, "wb") as f:
        pickle.dump(inputList, f)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=
                    "Remove first item in list of a pickle file to a csv file.")
    parser.add_argument("src", metavar="SRC", type=str,
                        help=("Pickle file with a single list."))
    parser.add_argument("dst", metavar="DST", type=str,
                        help=("csv file to write item into."))

    args = parser.parse_args()

    writeFirstPathToCSV(args.src, args.dst)
