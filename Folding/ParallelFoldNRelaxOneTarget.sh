#!/bin/sh

savefolder=`pwd`
numModels=20
alpha=1.61

runningMode=0
UsePerturbation=false

#parallelOptions=" --memfree 120G --load 92% "
parallelOptions=" --memfree 10G "

#if [[ -z "${DistanceFoldingHome}" ]]; then
#        echo "ERROR: Please set the environmental variable DistanceFoldingHome to installation folder of Folding"
#        exit 1
#fi

cmd=`readlink -f $0`
cmdDir=`dirname $cmd`

function Usage()
{
	echo $0 "[-d savefolder | -n numModels | -r runningMode | -a alpha | -o parallelOptions | -p ] seqFile predictedPairInfo [predictedPropertyInfo]"
	echo "	This script runs GNU Parallel to fold a protein on a single node using predicted distance/orientation/angles"
	echo "		Please make sure that GNU parallel has been installed"
	echo "	seqFile: the primary sequence file in FASTA format"
	echo "	predictedPairInfo: a Rosetta constraint file generated by GenRosettaPotential.sh or a PKL file for predicted distance/orientation info"
	echo "	predictedPropertyInfo: could be empty, a string 'cst' or a PKL file for predicted Phi/Psi angles"
	echo "	     when empty or 'cst', predictedPairInfo shall be a Rosetta constraint file instead of a PKL file"
	echo "	     Otherwise, both predictedPairInfo and predictedPropertyInfo shall be PKL files"
	echo "	-n: the number of models to be generated, default $numModels"
	echo "	-d: the folder for result saving, default current work directory"
	echo "	-r: 0 (default) or 1; if 0, fold only, otherwise fold+relax"
	echo "	-p: use perturbation in the folding stage, default No"
	echo "	-a: alpha value for DFIRE potential, default 1.61. If >20, a random value will be used"
	echo "	-o: extra options for GNU parallel, default $parallelOptions"
}

while getopts ":n:c:d:r:a:o:p" opt; do
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
		o )
		  #echo $OPTARG
		  parallelOptions=$OPTARG
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
	echo "ERROR: running mode can only be 0 or 1 "
	exit 1
fi

if [ $# -ne 3 -a $# -ne 2 ]; then
	Usage
	exit 1
fi

#program=${DistanceFoldingHome}/Scripts4Rosetta/PrintJob4FoldNRelaxOneTarget.sh
program=${cmdDir}/Scripts4Rosetta/PrintJob4FoldNRelaxOneTarget.sh
if [ ! -x $program ]; then
	echo "ERROR: invalid exectuable program $program"
	exit 1
fi

inFile=$1
if [ ! -f $inFile ]; then
	echo "ERROR: invalid input file for folding $inFile"
	exit 1
fi
target=`basename $inFile`
target=`echo $target | cut -f1 -d'.' `

seqLen=`tail -n +1 $inFile | wc -c`

pairMatrixFile=$2
if [ ! -f $pairMatrixFile ]; then
	echo "ERROR: invalid file for Rosetta constraints or predicted distance/orientation info: $pairMatrixFile"
	exit 1
fi

propertyFile="cst"
if [ $# -eq 3 ]; then
	propertyFile=$3
fi

if [ "$propertyFile" != "cst" ]; then
	if [ ! -f $propertyFile ]; then
		echo "ERROR: invalid file for predicted property: $propertyFile"
		exit 1
	fi
	if [ $seqLen -lt 450 ]; then
		potFolder=/dev/shm/cstDir4${target}-$$
	else
		potFolder=/tmp/cstDir4${target}-$$
	fi
	#${DistanceFoldingHome}/Scripts4Rosetta/GenRosettaPotential.sh -q $inFile -d $potFolder $pairMatrixFile $propertyFile
	${cmdDir}/Scripts4Rosetta/GenRosettaPotential.sh -q $inFile -d $potFolder $pairMatrixFile $propertyFile
	if [ $? -ne 0 ]; then
		#echo "ERROR: failed to run ${DistanceFoldingHome}/Scripts4Rosetta/GenRosettaPotential.sh -q $inFile -d $potFolder $pairMatrixFile $propertyFile"
		echo "ERROR: failed to run ${cmdDir}/Scripts4Rosetta/GenRosettaPotential.sh -q $inFile -d $potFolder $pairMatrixFile $propertyFile"
		exit 1
	fi
	if [ ! -d $potFolder ]; then
		#echo "ERROR: failed to run ${DistanceFoldingHome}/Scripts4Rosetta/GenRosettaPotential.sh -q $inFile -d $potFolder $pairMatrixFile $propertyFile"
		echo "ERROR: failed to run ${cmdDir}/Scripts4Rosetta/GenRosettaPotential.sh -q $inFile -d $potFolder $pairMatrixFile $propertyFile"
		exit 1
	fi
	fname=`basename $pairMatrixFile .predictedDistMatrix.pkl`
	cstFile=$potFolder/${fname}.pairPotential4Rosetta.SPLINE.txt
else
	cstFile=$pairMatrixFile
fi

if $UsePerturbation; then
	command="$program -d $savefolder -r $runningMode -a $alpha -n $numModels -p $inFile $cstFile cst"
else
	command="$program -d $savefolder -r $runningMode -a $alpha -n $numModels $inFile $cstFile cst"
fi

delay=1
if [ $seqLen -gt 100 ]; then
	delay=`expr $seqLen / 100 `
fi

parallelCmd="parallel --delay $delay $parallelOptions"

echo "$command | $parallelCmd"
$command | $parallelCmd

if [  "$propertyFile" != "cst" ]; then
	if [ -d $potFolder ]; then
		rm -rf $potFolder
		if [ $? -ne 0 ]; then
			echo "ERROR: failed to delete $potFolder"
			exit 1
		fi
	fi
fi
