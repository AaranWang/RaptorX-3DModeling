#!/bin/sh

if [[ -z "${DistFeatureHome}" ]]; then
        echo "ERROR: Please set environmental variable DistFeatureHome to the installation folder of BuildFeatures "
        exit 1
fi

if [ -z "${HHDIR}" ]; then
        echo "ERROR: please set environmental variable HHDIR to the install folder of HHblits"
        exit 1
fi

if [ ! -d $HHDIR ]; then
        echo "ERROR: invalid folder $HHDIR "
        exit 1
fi

if [ -z "${HHDB}" ]; then
        echo "ERROR: please set environmental variable HHDB to the sequence database used by HHblits"
        exit 1
fi

HHPkg=$DistFeatureHome/HHblitsWrapper/
#DB4Thread=$HHDBDIR/uniclust30_2017_10/uniclust30_2017_10
DB4Thread=$HHDBDIR/uniclust30/uniclust30
DB4HHMSA=$HHDBDIR/uniclust30/uniclust30

ResultDir=`pwd`

#JackPkg=$DistFeatureHome/EVAlign/
#DB4Jack=${JackDB}
DB4Jack=""

MSAmode=25
numCPUs=5
numAllowedJobs=5

function Usage()
{
        echo $0 "[ -d ResultDir | -m MSAmethod | -t SeqDB4Threading | -h SeqDB4HHblits | -j SeqDB4Jackhmmer | -n numJobs | -c numCPUs ] proteinListFile SeqDir"
        echo "	This script generates MSAs for contact/distance/orientation prediction using HHblits and optionally Jackhmmer for a list of proteins"
	echo "	proteinListFile: a file containing a list of proteins, each in one row"
	echo "	SeqDir: the folder for the sequences of proteins in the list file. Each sequence file shall be in FASTA format."
        echo "	-d: the folder for result saving, default current work directory "
        echo "	        The results will be saved to ResultDir/proteinName_OUT/"
        echo "	-m: an integer indicating MSA generation methods: 1, 2, 4, 8, 16 and their combination, default $MSAmode"
        echo "		1: run HHblits to generate MSA for local structure property prediction and for threading"
	echo "		2: run HHblits 2.0 to generate MSA for contact/distance/orientation prediction (obsolete)"
        echo "		4: run Jackhmmer to generate MSA for contact/distance/orientation prediction (slow, not recommended)"
	echo "		8: run HHblits 3.0 to generate MSA for contact/distance/orientation prediction"
        echo "		16: search MetaGenome database for each MSA generated by the above methods"
        echo " "
        echo "	SeqDB4Threading: sequence database used by HHblits for sequence profile generation, default $DB4Thread"
        echo "	SeqDB4HHblits: sequence database used by HHblits for MSA generation for contact/distance prediction, default $DB4HHMSA"
        echo "	SeqDB4Jackhmmer: sequence database used by Jackhmmer for MSA generation for contact/distance prediction"
	echo "		When not provided by user, this script will use the database set by the environmental variable JackDB"
	echo "		So please make suer that JackDB is properly set up if you do not want to provide a protein sequence database"
	echo "	-n: the number of sequences to be simultaneously run, default $numAllowedJobs "
        echo "	-c: the number of CPUs to be used for HHblits and Jackhmmer for a single sequence, default $numCPUs"
}

while getopts ":m:d:t:h:j:c:n:" opt; do
        case ${opt} in
                t )
                  DB4Thread=$OPTARG
                  ;;
                m )
                  MSAmode=$OPTARG
                  ;;
                d )
                  ResultDir=$OPTARG
                  ;;
                h )
                  DB4HHMSA=$OPTARG
                  ;;
                j )
                  DB4Jack=$OPTARG
                  ;;
                c )
                  numCPUs=$OPTARG
                  ;;
		n )
		  numAllowedJobs=$OPTARG
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

if [ $# -ne 2 ]; then
        Usage
        exit 1
fi

if [[ -z "$DB4Jack" ]]; then
	DB4Jack=$JackDB
fi

proteinList=$1
if [ ! -f $proteinList ]; then
	echo "ERROR: invalid file for protein list $proteinList"
	exit 1
fi

SeqDir=$2
if [ ! -d $SeqDir ]; then
	echo "ERROR: invalid folder for query sequences $SeqDir"
	exit 1
fi

cmd=`readlink -f $0`
cmdDir=`dirname $cmd`

program=$cmdDir/BuildMSAs.sh

if [[ -z "$DB4Jack" ]]; then
	command="cat $proteinList | parallel -j $numAllowedJobs $program -d $ResultDir -m $MSAmode -c $numCPUs -t $DB4Thread -h $DB4HHMSA $SeqDir/{}.fasta"
else
	command="cat $proteinList | parallel -j $numAllowedJobs $program -d $ResultDir -m $MSAmode -c $numCPUs -t $DB4Thread -h $DB4HHMSA -j $DB4Jack $SeqDir/{}.fasta"
fi

$command
if [ $? -ne 0 ]; then
	echo "ERROR: failed to run $command"
	exit 1
fi