#! /bin/bash

function morecells () {
    vmtksurfacereader -ifile $1 --pipe \
    vmtksurfacesubdivision -method butterfly \
    -ofile $2
}

function smooth () {
    vmtksurfacereader -ifile $1 --pipe \
    vmtksurfacekiteremoval --pipe \
    vmtksurfacesmoothing -iterations 30 -passband 0.1 \
    -ofile $2 --pipe \
    vmtksurfaceviewer
}

function triangle () {
    vmtksurfacereader -ifile $1 --pipe \
    vmtksurfacetriangle -ofile $2 --pipe \
    vmtksurfaceviewer
}

function fixdegeneratetriangles () {
    vmtksurfacereader -ifile $1 --pipe \
    vmtksurfacesubdivision -method loop -ofile $2 --pipe \
    vmtksurfaceviewer
}

function clipauto () {
    vmtksurfacereader -ifile $1 --pipe \
    vmtkcenterlines --pipe \
    vmtkendpointextractor -numberofendpointspheres 1 --pipe \
    vmtkbranchclipper --pipe \
    vmtksurfaceconnectivity -cleanoutput 1 --pipe \
    vmtkrenderer --pipe \
    vmtksurfaceviewer -display 0 -ofile $2 --pipe \
    vmtksurfaceviewer -i @vmtksurfacereader.o -opacity 0.25 -display 1
}

function clipmanu() {
    vmtksurfaceclipper -ifile $1 \
    -ofile $2
}

function extend_bn () {
    vmtksurfacereader -ifile $1 --pipe \
    vmtkcenterlines -seedselector openprofiles -endpoints 1 --pipe \
    vmtkflowextensions -adaptivelength 1 -extensionratio 10. -extensionmode \
    boundarynormal -normalestimationratio 1 -interactive 0 --pipe \
    vmtksurfaceconnectivity -cleanoutput 1 --pipe \
    vmtksurfacetriangle --pipe \
    vmtksurfacewriter -ofile $2 --pipe \
    vmtksurfaceviewer
}

function extend_cl () {
    vmtksurfacereader -ifile $1 --pipe \
    vmtkcenterlines -seedselector openprofiles -endpoints 1 --pipe \
    vmtkflowextensions -adaptivelength 1 -extensionratio 10. -extensionmode \
    centerlinedirection -normalestimationratio 1 -interactive 0 --pipe \
    vmtksurfaceconnectivity -cleanoutput 1 --pipe \
    vmtksurfacetriangle --pipe \
    vmtksurfacewriter -ofile $2 --pipe \
    vmtksurfaceviewer
}

function mesh () {
    name="${2%.*}"
    vmtksurfacereader -ifile $1 --pipe \
    vmtkcenterlines -endpoints 1 -seedselector openprofiles --pipe \
    vmtkdistancetocenterlines -useradius 1 --pipe \
    vmtkmeshgenerator -elementsizemode edgelengtharray \
    -edgelengtharray DistanceToCenterlines -edgelengthfactor 0.3 \
    -maxedgelength 1. \
    -ofile $2 -remeshedsurfacefile ${name}.vtp --pipe \
    vmtkmeshviewer 
}

function remeshsurf () {
    vmtksurfacereader -ifile $1 --pipe \
    vmtkcenterlines -seedselector openprofiles -endpoints 1 --pipe \
    vmtkdistancetocenterlines -useradius 1 --pipe \
    vmtksurfaceremeshing -elementsizemode edgelengtharray \
    -edgelengtharray DistanceToCenterlines -edgelengthfactor 0.3 --pipe \
    vmtksurfacetriangle -ofile $2 --pipe \
    vmtksurfaceviewer
}

function remeshsurf2 () {
    vmtksurfacereader -ifile $1 --pipe \
    vmtksurfaceremeshing -area 0.1 -minareafactor 0.2 --pipe \
    vmtksurfaceconnectivity -cleanoutput 1 --pipe \
    vmtksurfacetriangle -ofile $2 --pipe \
    vmtksurfaceviewer
}

read -p "Input patient: " dir
    cd $dir 
read -p "Input input filepath: " infile
read -p "Input output filepath: " outfile
while true; do
    read -p "Morecells/Smooth/Triangle/Fix-Degenerate-Triangles/Clip-Auto/Clip-Manual/Extend-BN/Extend-CL/Mesh/Remesh-Surface/Remesh-Surface-2 or Exit? (0/1/2/3/4/5/6/7/8/9/a/e): " yn
        case $yn in
            [0]* ) morecells $infile $outfile;;
            [1]* ) smooth $infile $outfile;;
            [2]* ) triangle $infile $outfile;;
            [3]* ) fixdegeneratetriangles $infile $outfile;;
            [4]* ) clipauto $infile $outfile;;
            [5]* ) clipmanu $infile $outfile;;
            [6]* ) extend_bn $infile $outfile;;
            [7]* ) extend_cl $infile $outfile;;
            [8]* ) mesh $infile $outfile;; 
            [9]* ) remeshsurf $infile $outfile;;
            [Aa]* ) remeshsurf2 $infile $outfile;;
            [Ee]* ) exit;;
            * ) echo "invalid option";;
        esac
    done
