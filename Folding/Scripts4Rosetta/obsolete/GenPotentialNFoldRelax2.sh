#!/bin/sh

savefolder=`pwd`
numModels=1
runningMode=0
UsePerturbation=False

alpha=1.61

if [[ -z "${DistanceFoldingHome}" ]]; then
        echo "ERROR: Please set the environmental variable DistanceFoldingHome to installation folder of Folding"
        exit 1
fi

function Usage()
{
	echo "$0 [ -d savefolder | -n numModels | -r runningMode | -a alpha | -p ] inFile predictedPairInfo predictedPropertyInfo"
	echo "	This script folds a protein and/or relaxes 3D models using predicted information"
	echo "	inFile: a sequence file in FASTA format (each residue represented as one upper case letter) or a PDB file"
	echo "	predictedPairInfo: a Rosetta constraint file generated by GenRosettaPotential.sh or a PKL file for predicted distance/orientation information"
        echo "	predictedPropertyInfo: cst or a PKL file for predicted Phi/Psi angles"
        echo "	     When it is cst, predictedPairInfo shall be a Rosetta constraint file instead of a PKL file"
	echo "	     Otherwise, both predictedPairInfo and predictedPropertyInfo shall be PKL files for predicted distance/orientation/angles"
        echo "	-n: the number of models to be generated, default $numModels"
        echo "	-d: the folder for result saving, default current work directory"
        echo "	-r: specify running modes: 0 (fold only), 1 (fold and relax), 2 (relax only), default $runningMode"
	echo "	     When 2 is used, inFile shall be a structure file; otherwise inFile shall be a seq file"
	echo "	-a: alpha used in DFIRE potential, default $alpha"
	echo "	-p: use perturbation at the folding stage, default No"
}

while getopts ":n:d:r:a:p" opt; do
        case ${opt} in
                n )
                  numModels=$OPTARG
                  ;;
                d )
                  savefolder=$OPTARG
                  ;;
                r )
                  runningMode=$OPTARG
                  ;;
		p )
		  UsePerturbation=True
		  ;;
		a )
		  alpha=$OPTARG
		  ;;
                \? )
                  echo "Invalid Option: -$OPTARG" 1>&2
                  exit 1
                  ;;
                : )
                  echo "Invalid Option: -$OPTARG requires an argument" 1>&2
                  exit 1
                  ;;
        esac
done
shift $((OPTIND -1))

if [ $# -lt 3 ]; then
	Usage
	exit 1
fi

date

inFile=$1
if [ ! -f $inFile ]; then
        echo "ERROR: invalid input file $inFile"
        exit 1
fi

pairMatrixFile=$2
if [ ! -f $pairMatrixFile ]; then
	echo "ERROR: invalid file for predicted distance/orientation info: $pairMatrixFile"
	exit 1
fi

if [ ! -d $savefolder ]; then
	mkdir -p $savefolder
fi

machine=`hostname`

propertyFile=$3
if [ "$propertyFile" == "cst" ]; then
        ## treat pairMatrixFile as a constraint file instead of a PKL file
        cstfile=$pairMatrixFile

elif [ "$machine" != "raptorx10.uchicago.edu" ]; then
        if [ ! -f $propertyFile ]; then
                echo "ERROR: invalid file for predicted property: $propertyFile"
                exit 1
        fi

	target=`basename $pairMatrixFile `
	target=`echo $target | cut -f1 -d'.'`
        ## create a temporary cstfolder
        cstfolder=$(mktemp -d -t tmpCstDir4${target}-XXXXXXXXXX)
        cstfolder=`readlink -f $cstfolder`
        $DistanceFoldingHome/Scripts4Rosetta/GenRosettaPotential.sh -a $alpha -d $cstfolder $pairMatrixFile $propertyFile
        cstfile=$cstfolder/$target.pairPotential4Rosetta.SPLINE.txt
else
	cstfile="$pairMatrixFile -I alpha=$alpha,phipsi=$propertyFile"
fi

if [ "$machine" == "raptorx10.uchicago.edu" ]; then
	program=$DistanceFoldingHome/Scripts4Rosetta/FoldNRelax2.py
	if [ $runningMode -eq 2 ]; then
		program=$DistanceFoldingHome/Scripts4Rosetta/Relax2.py
	fi
else
	program=$DistanceFoldingHome/Scripts4Rosetta/FoldNRelax.py
	if [ $runningMode -eq 2 ]; then
		program=$DistanceFoldingHome/Scripts4Rosetta/Relax.py	
	fi
fi

if [ ! -f $program ]; then
	echo "ERROR: incorrect program $program"
	exit 1
fi

i=0
while [ $i -lt $numModels ];
do
	if [ $runningMode -eq 1 -o $runningMode -eq 2 ]; then
        	python $program $inFile $cstfile -e 1.5 -s $savefolder

	elif [ $runningMode -eq 0 ]; then
		if (( $UsePerturbation )); then
        		python $program $inFile $cstfile -s $savefolder -q -p
		else
        		python $program $inFile $cstfile -s $savefolder -q
		fi
	else
		echo "ERROR: incorrect running mode specified"
		exit 1
	fi
        i=`expr $i + 1`
done

if [ "$propertyFile" != "cst" ]; then
        rm -rf $cstfolder
fi

date
