#!/bin/sh

savefolder=`pwd`
numModels=300
runningMode=0

alpha=1.61
UsePerturbation=false

function Usage()
{
	echo $0 "[ -d savefolder | -n numModels | -r runningMode | -a alpha | -p] inFile predictedPairInfo [predictedPropertyInfo]" 
	echo "	This script prints out a list of jobs to be submitted to a cluster or GNU parallel"
	echo "	inFile: the primary sequence file in FASTA format or a PDB file for an initial model"
	echo "	predictedPairInfo: a Rosetta constraint file generated by GenRosettaPotential.sh or a PKL file for predicted distance and orientation"
	echo "	predictedPropertyInfo: empty or a PKL file for predicted Phi/Psi angles"
	echo "		when not specified, predictedPairInfo shall be Rosetta constraint file; otherwise a PKL file"
	echo "	-d: the folder for result saving, default current work directory"
	echo "	-n: the number of models to be generated, default $numModels"
	echo "	-r: running mode: 0 (fold only) or 1 (fold+relaxation), default $runningMode"
	echo "	-a: alpha used in DFIRE potential, default $alpha"
	echo "	-p: use perturbation in energy minization, default $UsePerturbation"
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
		a )
		  alpha=$OPTARG
		  ;;
		p )
		  UsePerturbation=true
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

if [ $runningMode -ne 0 -a $runningMode -ne 1 ]; then
	echo "ERROR: invalid running mode"
	exit 1
fi

if [ $# -lt 2 -o $# -gt 3 ]; then
	Usage
	exit 1
fi

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

propertyFile='cst'
if [ $# -eq 3 ]; then
	propertyFile=$3
fi
if [ "$propertyFile" != "cst" ]; then
	if [ ! -f $propertyFile ]; then
		echo "ERROR: invalid file for predicted property info: $propertyFile"
		exit 1
	fi
fi

program=${DistanceFoldingHome}/Scripts4Rosetta/GenPotentialNFoldRelax.sh
i=0
while [ $i -lt $numModels ];
do
	if $UsePerturbation; then
        	echo "$program -r $runningMode -d $savefolder -a $alpha -p $inFile $pairMatrixFile $propertyFile"
	else
        	echo "$program -r $runningMode -d $savefolder -a $alpha $inFile $pairMatrixFile $propertyFile"
	fi
        i=`expr $i + 1 `
done
