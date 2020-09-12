# README #


### What is this repository for? ###

RaptorX predicts protein contact/distance/orientation and local structure properties (e.g, secondary structure and phi/psi angles) by deep convolutional residual networks.
It also predicts the 3D structure of a protein sequence using predicted distance/orientation and phi/psi angles.
It is mainly tested on the Linux distribution CentOS (>6.0) and Python 2.7, but can work with Python 3 by creating a virtual environment.
A version supporting Python 3 and tensorflow will be available in a few months. 
This package is also incorporated into our protein structure prediction web server at http://raptorx.uchicago.edu/, which is publicly available for both academia and industry.
If you only want to predict structures for several protein sequences, it is more convenient to use our web server instead of installing this package.

* Version

4.0

* There is no restriction on the usage of this package, but without explicit permission, it shall not be used for commercial purpose and to set up a similar web server for protein folding.

### How to set up? ###

Download this package by "git clone" and install it anywhere in your own account, e.g., $HOME/RaptorX-3DModeling/.
It contains the following files and subfolders (and a few others):

BuildFeatures/

DL4DistancePrediction4/

DL4PropertyPrediction/

Folding/

params/

raptorx-external.sh

README.md

Server/

This RaptorX package consists of 4 major modules: BuildFeatures/ for generating multiple sequence alignment (MSAs) and input features for angle/contact/distance/orientation prediction,
DL4DistancePrediction4/ for contact/distance/orientation prediction, DL4PropertyPrediction/ for local structure property prediction, and Folding/ for building 3D models.

To predict contact/distance/orientation and fold a protein, you may simply run RaptorX-3DModeling/Server/RaptorXFolder.sh, but before doing this some external packages and databases shall be installed and configured.

## Required external packages for all modules ##

1) anaconda or miniconda for Python 2.7

If you have not installed any anaconda or miniconda, you may directly install anaconda or miniconda for Python 2.7.
If you have already installed anaconda/miniconda for Python 3, you may create a virtual enviroment RaptorX by running "conda create --name RaptorX python=2". 
Afterwards, switch to this virtual environment to install the required packages and run RaptorX. 

Install numpy by "conda install numpy".
Install msgpack-python by "conda install -c anaconda msgpack-python"; it may not work if you intall it through pip.

2) Biopython (https://biopython.org/)

Needed for both contact/distance/orientation predicton and 3D model building
install by running "pip install biopython==1.76"
A newer version of Biopython may not support Python 2.7.

## Required packages for contact/distance/orientation/angle prediction ##

1) Pillow

Needed for visualizing predicted contact and distance; install by running "pip install Pillow"

2) pygpu and Theano 1.0 (http://deeplearning.net/software/theano/install.html)

Needed for train and run deep learning models; install by running "conda install numpy scipy mkl" and then "conda install theano pygpu" .

Please make sure that the CUDA toolkits and CUDNN library have been installed on your machine with GPUs.
Set the environment variable CUDA_ROOT to where cuda is installed, e.g., export CUDA_ROOT=/usr/local/cuda. 
Make sure that the header and lib64 files of CUDNN are in CUDA_ROOT/include and CUDA_ROOT/lib64, respectively. 
(Theano 1.0 works with CUDA 10.0 and cudnn 7.6. Other versions of CUDA and CUDNN may also work)

3) shared_ndarray (https://github.com/crowsonkb/shared_ndarray.git)

Needed for train and run deep learning models for distance/orientation prediction.
Download by "git clone https://github.com/crowsonkb/shared_ndarray.git";
cd to shared_ndarray/ and then run "python setup.py install".

## Required tools and sequence databases for MSA generation ##

1) Install HHblits for MSA generation (https://github.com/soedinglab/hh-suite)

In addition to the HHsuite package itself, please download a sequence database specific to HHsuite and unpack it into a folder, 
e.g. UniRef30_2020_03_hhsuite.tar.gz at http://wwwuser.gwdg.de/~compbiol/uniclust/2020_03/.

2) Install EVcouplings for generating MSAs by jackhmmer (optional, but not recommended since it is too slow)

It is available at https://github.com/debbiemarkslab/EVcouplings . Although installing the whole package, only the MSA generation module will be used.
Step 1: Download the package by running "git clone https://github.com/debbiemarkslab/EVcouplings.git". Suppose that it is located at $HOME/EVcouplings. 
Step 2: Run "conda create -n evfold anaconda python=3" to create a virtual environment and then switch to this environment by running "conda activate evfold".
Step 3: cd to $HOME/EVcouplings and run "python setup.py install" to install the whole package.

Note that EVcouplings runs on python 3 while this version of RaptorX runs on python 2.
Without jackhmmer, you may still run RaptorX by generating MSAs using HHblits only.
The sequence database for jackhmmer is uniref90.fasta, which can be downloaded from UniProt.

3) Metagenome data (optional)

Download the data file metaclust_50.fasta at https://metaclust.mmseqs.org/current_release/ and install it somewhere.

4) Revise the file RaptorX-3DModeling/raptorx-external.sh to setup the path information for the above MSA building tools and databases.

## Required packages for building protein 3D models ##

1) PyRosetta (http://www.pyrosetta.org/dow)

Needed to fold a protein sequence from predicted distance/orientation and phi/psi angles.
Please download the version supporting Python 2.7.
Afterwards, cd to PyRosetta4.Release.python27.linux.release-224/setup/ and run "python setup.py install" where PyRosetta4.Release.python27.linux.release-224 is the folder of the unpacked package.

2) GNU parallel (optional, but recommended for running folding jobs on a Linux workstation)

Some scripts in RaptorX-3DModeling/Folding/ (e.g., ParallelFoldNRelaxOneTarget.sh and SRunFoldNRelaxOneTarget.sh) use GNU parallel to run multiple folding jobs on one or multiple computers.
Run "which parallel" to see if GNU parallel is available or not.
If GNU parallel cannot be installed, you may still run folding jobs using other scripts.

## Configuration and export of environment variables ##

1) ModelingHome: This is where the whole package is installed, e.g., $HOME/RaptorX-3DModeling.
Please add ModelingHome to the environmental variable PYTHONPATH.

2) DistFeatureHome=$ModelingHome/BuildFeatures/ for generating MSAs and input features.

3) DL4PropertyPredHome=$ModelingHome/DL4PropertyPrediction/ for predicting local structure properties such as Phi/Psi angles.

4) DL4DistancePredHome=$ModelingHome/DL4DistancePrediction4/ for contact/distance/orientation prediction. 

5) DistanceFoldingHome=$ModelingHome/Folding/ for building 3D models

6) Please revise the sequence database path information and HHblits install folder in $ModelingHome/raptorx-external.sh 
and then add ". $ModelingHome/raptorx-external.sh " to the .bashrc file in your own Linux account to set enviromental variables related to MSA generation.

Supposing that the RaptorX-3DModeling package is located at $HOME/RaptorX-3DModeling/,
below is an example configuration that can be pasted to the .bashrc file if you are using the bash shell.

export ModelingHome=$HOME/RaptorX-3DModeling/

. $ModelingHome/raptorx-external.sh

export DistFeatureHome=$ModelingHome/BuildFeatures/

export DL4DistancePredHome=$ModelingHome/DL4DistancePrediction4/

export DL4PropertyPredHome=$ModelingHome/DL4PropertyPrediction/

export DistanceFoldingHome=$ModelingHome/Folding/

export PYTHONPATH=$ModelingHome:$PYTHONPATH

export PATH=$ModelingHome/bin:$PATH

export CUDA_ROOT=/usr/local/cuda/

If you are using csh shell, you may add a similar setting to the file .cshrc in your home directory.

## Install deep learning models for contact/distance/orientation/angle prediction ##

The deep learning model files for contact/distance/orientation prediction are big (each 100-200M). They are available at http://raptorx.uchicago.edu/download/ .

1) The package RXDeepModels4DistOri-FM.tar.gz has 6 models for contact/distance/orientation/ prediction. Unpack it and place all the deep model files (ending with .pkl) at $DL4DistancePredHome/models/

1) The package RXDeepModels4Property.tar.gz has 3 deep models for Phi/Psi angle prediction. Unpack it and place all the deep model files (ending with .pkl) at $DL4PropertyPredHome/models/

## Basic Usage

You may run shell script RaptorXFolder.sh in RaptorX-3DModeling/Server/ to predict angle/contact/distance/orientation and/or fold a protein. 
The input can be a protein sequence in FASTA format (ending with .fasta or .seq) or an MSA file in a3m format (ending with .a3m).
In the input file, an amino acid shall be represented by a capital letter instead of a 3-letter code.
Run RaptorXFolder.sh (and other shell scripts in this package) without any arguments will show its help information. Below are some scenarios.

1) When you already have a multiple sequence alignment in a3m format, please use option "-m 0";

2) When you only want to predict angle/contact/distance/orientation but not 3D models, please use option "-n 0";

3) When you do not want to generate MSAs using jackhmmer, you may use option "-m 9" (without using metagenome data) or "-m 25" (using metagenome data). 
Note that jackhmmer usually is slow, so it is not recommended for MSA generation.

Ideally, RaptorXFolder.sh shall run on a computer with GPUs and a reasonable number of CPUs.
It takes minutes (rarely a couple of hours) to generate MSAs for a protein and several (or at most dozens of) minutes to predict distance/orientation on a single GPU.
The running time for building 3D models from predicted angle/distance/orientation depends on the protein sequence length and whether or not to run relaxation.
When relaxation is not applied, on a single CPU it takes <1 hour to build one 3D model for a protein of 300 residues and 2-3 hours for a protein of 1000 residues. 
However, when relaxation is applied, it may increase the running time by 3 or 4 times. 
Usually one hundred 3D models shall be generated, but this number may be reduced if the predicted distance/orientation is of high quality.
When the protein under prediction is big, GPU and CPU memory may be an issue. 
For a protein of >1000 residues, it may need >12G GPU memory to predict distance/orientation and 10G CPU memory to fold (and relax) one 3D model.


All the result files are saved to a folder target_OUT/ where target is the protein name containing the following subfolders:

1) target_contact/ contains MSAs and input features for distance/orientation prediction;

2) target_thread contains files for Phi/Psi prediction (which are also used for threading);

3) DistancePred/ contains predicted distance/orientation/contact and their visualization;

4) PropertyPred/ contains predicted Phi/Psi angles and secondary structure;

5) target-RelaxResults/ contains all generated decoys;

6) target-SpickerResults/ contains the clustering results of the decoys.

It is possible to run RaptorXFolder.sh on several machines, each in charge of one major module (MSA generation, feature generation and distance/orientation prediction, 3D model building),
without requiring you to manually copy data among different machines. This will be explained later.

## References

1. Distance-based protein folding powered by deep learning. PNAS, August 2019. A 2-page abstract also appeared at RECOMB2019 in April 2019.

2. Analysis of distance-based protein structure prediction by deep learning in CASP13. PROTEINS, 2019.

3. Accurate De Novo Prediction of Protein Contact Map by Ultra-Deep Learning Model. PLoS CB, Jan 2017

4. Folding Membrane Proteins by Deep Transfer Learning. Cell Systems, September 2017.

## Detailed Usage

* How to generate multiple sequence alignments (MSA)

HHblits and Jackhmmer are two popular tools for protein sequence homology search.
Enclosed in this package (located in folder BuildFeatures/) there are some scripts that call HHblits and Jackhmmer to build MSAs.

1) To generate MSA for Phi/Psi prediction and threading only, run "BuildMSAs.sh -d ResultDir -m 1 SeqFile" where ResultDir is the folder for result saving.
Helpers/BuildMSA4Threading.sh is another script for this purpose.

2) To generate a single MSA from a protein sequence for contact/distance prediction, you may use BuildFeatures/HHblitsWrapper/BuildMSA4DistPred.sh and/or BuildFeatures/EVAlign/BuildMSAByJack.sh .
Note that BuildFeatures/EVAlign/BuildMSAByJack.sh is usually much slower than BuildMSA4DistPred.sh.

3) To generate MSAs for a single protein for contat/distance/orientation prediction, you may use BuildFeatures/BuildMSAs.sh. 
This script may generate multiple MSA files for a single protein depending on your input options.
For example, to generate MSA for Phi/Psi and contact/distance prediction, you may run "BuildMSAs.sh -d ResultDir -m 9 SeqFile" or "BuildMSAs.sh -d ResultDir -m 25 SeqFile"
The ResultDir contains two subfolders XXX_contact and XXX_thread where XXX is the protein name. XXX_contact has MSA files for contact/distance prediction and XXX_thread has an MSA file for Phi/Psi prediction.
By default BuildMSAs.sh will not use jackhmmer to generate MSAs since it is slow, but you may enable it by adding 4 to the option value of "-m".

4) To generate MSAs for multiple proteins, you may use BatchBuildMSAs.sh. A set of MSAs will be generated for an individual protein.
By default, BatchBuildA3M.sh will not use jackhmmer to generate MSAs since it is slow. 

5) To generate input features from one MSA for distance/orientation prediction, you may run BuildFeatures/GenDistFeaturesFromMSA.sh
At least one GPU is needed to run CCMpred efficiently. Otherwise it may take a long time to generate features.

6) To directly generate input features for contact/distance/orientation prediction from protein sequences,
you may run BuildFeatures.sh for a single protein or BatchBuildFeatures.sh for multiple proteins.
These two scripts call BuildMSAs.sh to build MSAs and then derive input features from MSAs.
At least one GPUs is needed to efficiently run CCMpred. When there are no GPUs, it may take a long time on CPUs.

* How to predict contact/distance/orientation from MSAs or input features

GPUs will be needed and CUDA shall be installed.
Some scripts such as PredictPairRelationRemote.sh and PredictPairRelation4Server.sh may run on a computer without GPUs as long as you may ssh (without password) to a remote computer with GPUs which have RaptorX installed.

1) To predict contact/distance/orientation from a single MSA file in a3m format, you may use DL4DistancePrediction4/Scripts/PredictPairwiseRelationFromMSA.sh
Note that the 1st sequence in the A3M file shall be the query sequence without any gaps.
One result file XXX.predictedDistMatrix.pkl will be generated that can be opened by cPickle.

2) To predict contact/distance/orientation from a list of MSA files (each protein has one MSA file in this list), first use BuildFeatures/BatchGenDistFeaturesFromMSAs.sh to generate input feature files from all MSA files
and then run DL4DistancePrediction4/Scripts/PredictPairwiseRelation4Inputs.sh. This is much faster than running PredictPairwiseRelationFromMSA.sh on each MSA file separately.

3) To predict contact/distance/orientation from several MSAs generated by BuildMSAs.sh for a single protein, first run BuildFeatures/GenDistFeatures4OneProtein.sh and then DL4DistancePrediction4/Scripts/PredictPairwiseRelation4OneProtein.sh

4) To predict contact/distance/orientation for multiple proteins, each of which has a set of MSAs generated by BuildMSAs.sh, first run BuildFeatures/GenDistFeatures4OneProtein.sh or GenDistFeatures4MultiProteins.sh 
and then DL4DistancePrediction4/Scripts/PredictPairwiseRelation4Proteins.sh 

5) To print out contact matrix from predicted distance/orientation files, use PrintContactPrediction.sh or BatchPrintContactPrediction.sh in DL4DistancePrediction4/Scripts/

Note that the input feature files generated by GenDistFeaturesFromMSAs.sh and BatchGenDistFeaturesFromMSAs.sh and the predicted distance/orientation file may be very large for a large protein.
To save disk space, please avoid generating input feature files or predicting distance/orientation for too many proteins in a batch.

* How to predict protein local structure properties such as Phi/Psi angles and secondary structure

Several scripts in /home/jinbo/RaptorX-3DModeling/DL4PropertyPrediction/Scripts/ can be used, e.g., PredictPropertyFromMSA.sh, PredictPropertyFromHHMs.sh, PredictProperty4OneProtein.sh and PredictProperty4Proteins.sh
Some scripts such as PredictPropertyRemote.sh and PredictProperty4Server.sh may run on a remote computer with GPUs and to which you may ssh without password.

** How to build 3D models from predicted angle/distance/orientation files

1) To fold a protein from its primary sequence or an MSA without manually run the intermediate steps, you may run RaptorX-3DModeling/Server/RaptorXFolder.sh

2) When you already have predicted distance/orientation files (ending with .predictedDistMatrix.pkl) and Phi/Psi file (ending with .predictedProperties.pkl), you may use them to fold a protein by several scripts.
In RaptorX-3DModeling/Folding/, there are LocalFoldNRelaxOneTarget.sh, ParallelFoldNRelaxOneTarget.sh, SRunFoldNRelaxOneTarget.sh and SlurmFoldNRelaxOneTarget.sh, developed for different machine types (e.g., Linux workstation and slurm cluster)
In aptorX-3DModeling/Folding/Scripts4Rosetta/, there are FoldNRelaxOneTarget.sh, FoldNRelaxTargets.sh, and RelaxOneTarget.sh, which mainly run on a Linux workstation.

## Advanced Usage (to be updated)

* Run scripts on several computers without manually copying files

Suppose that you have access to three machines: the 1st one has a small number of CPUs but not any GPUs, the 2nd one has GPUs but very few CPUs, and the third one has many CPUs but not GPUs. 
You may start RaptorXFolder.sh on the 1st machine, which will then automatically ship the GPU tasks to the 2nd machine and the folding tasks to the 3rd machine. 
During this process, you do not need to manually copy files and results among machines. 
To fullfil this, you shall install this RaptorX package (or a portion of it) on the three machines so that on the 1st one you may run MSA generation,
on the 2nd one you can run GPU tasks (e.g., CCMpred and distance/orientation prediction) and on the 3rd one you may run 3D model building. 

To run GPU tasks at a remote machine, please create one file (e.g., GPUMachines.txt) to specify the remote machines which have GPUs and to which you may ssh without password. 
See an example file in RaptorX-3DModeling/params/. A line in this file looks like "raptorx9.uchicago.edu LargeRAM on" or "raptorx5.uchicago.edu SmallRAM off" 
where the three fields are the computer name, GPUs of a small RAM (<=12G) or a large RAM, and enabled/disabled, respectively.
You may save this file at a default location (i.e., RaptorX-3DModeling/params/GPUMachines.txt) or other places.

To run folding jobs at a remote machine, you just need to specify a remote account while running RaptorXFolder.sh. Again please make sure that you may ssh and scp to this remote account without password.  

## Test

1) Generate input feature files for contact/distance prediction from an MSA file in a3m format:

BuildFeatures/GenDistFeaturesFromMSA.sh -o Test_Feat BuildFeatures/example/1pazA.a3m

Three feature files shall be generated in Test_Feat/: 1pazA.inputsFeatures.pkl, 1pazA.extraCCM.pkl and 1pazA.a2m. 
Meanwhile, the first two .pkl files are needed for contact/distance/orientation prediction and 1pazA.a2m may be needed by very few deep models. 

2) Predict distance/orientation from feature files:

DL4DistancePrediction4/Scripts/PredictPairwiseRelation4OneInput.sh -d ./Test_Dist Test_Feat/1pazA.inputsFeatures.pkl

The result file Test_Dist/1pazA.predictedDistMatrix.pkl should be generated.

3) Generate predicted contact matrix in text format:

To print out predicted contact matrix in text format, run "DL4DistancePrediction4/Scripts/PrintContactPrediction.sh Test_Dist/1pazA.predictedDistMatrix.pkl".
This will generate two text files 1pazA.CASP.rr and 1pazA.CM.txt.


** How to run the training (to be updated)

To train a contact/distance prediction deep network, please go to $DL4DistancePredHome/Work/ and run the shell script TrainCbCbEC25CL51-Adam.sh.
Before running the shell script, please make sure that you set the path of the training and test data correctly.
On raptorx4, raptorx5 and raptorx6 machines, you may simply link the data path to your own work directory. Please read TrainCbCbEC25CL51-Adam.sh for instructions. 
Please do not use cuda0 on thee three machines to run the training algorithm. They are reserved for our web server.


### Develop your own deep network ###


To incorporate your own deep network architeture into the contact/distance prediction module, please follow the below procedure:


1) In Model4PairwisePrediction.py, find the sentence starting with "matrixConv=ResNet". 
Let XXYY denote your own network, then you may change this sentence to the following code.


if modelSpecs['network'] == 'XXYY':


        matrixConv=XXYY(....)


else:


        matrixConv=ResNet(rng, input=input_2d, n_in=n_input2d, n_hiddens=n_hiddens_matrix, n_repeats=matrix_repeats, halfWinSize=hwsz_matrix, mask=mask_matrix, activation=modelSpecs['activation'], batchNorm=modelSpecs['batchNorm'])


Note that your implementation of XXYY shall have the same input and output format as our ResNet implementation.
XXYY shall also contain the following variables: output, n_out, params, paramL2 and paramL1. Meanwhile, params, paramL2 and paramL1 are the list of model parameters and their norms.
output and n_out in XXYY shall be consistent with output and n_out in ResNet.
In addition, it is better to use the BatchNormLayer class in ResNet4Distance.py and the convolution layer we implemented.
If you want to use other batch normalization implementation, please make sure 1) calculate mean and standard deviation for each protein instead of each minibatch; 2) remove the impact of the zero-padding.
Please read our batch normalization code for details.


2) In config.py, please add 'XXYY' to allNetworks, which is a list of all allowed network architectures.


3) If needed, in InitializeModelSpecs() (of config.py), please add some code to set the default architecture parameters for your own network.


4) If needed, please revise ParseCommandLine.py to read in your own network architecture information from the shell script Work/TrainCbCbEC25L51-Adam.sh


5) Revise Work/TrainCbCbEC25L51-Adam.sh accordingly.


Currently two minibatches may have different protein lengths. In the same minibatch, all the proteins are aligned at the right bottom corner and zero padded to have the same length.
We use a mask matrix to indicate the zero-padding pattern at the left and top of a contact matrix.
If you use pooling layers, please make sure that you change the mask matrix correctly after every pooling.
The mask matrix has a smaller shape than the contact matrix. For the 2D convolution, the mask matrix has shape (batchSize, maxProteinLen, maxProteinLen-minProteinLen) where maxProteinLen and minProteinLen are the maximum and minimum protein lengths in a minibatch. For the 1D convolution, the mask matrix has shape (batchSize, maxProteinLen - minProteinLen).


### Who do I talk to? ###


Jinbo Xu at jinboxu@gmail.com