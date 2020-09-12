import os
import sys
import numpy as np
import getopt
import random
import shutil
import tempfile
import socket

from pyrosetta import *
from pyrosetta.teaching import *
from pyrosetta.rosetta import *

from pyrosetta.rosetta.protocols.minimization_packing import MinMover

#from ScoreOneModel import GetScore
#from ScoreOneModel import PrintScore

def Usage():
	print 'python FoldNRelax.py inputFile flexiblRegions [ -n ncycles ] [-s savefolder ] '
	print '       inputFile: an initial PDB file'
	print '	      flexibleRegions: the regions that allow changes, e.g., 3-6, 100-110'
	print '       -n: the number of iterations for each MinMover (default 1000)'
	print '	      -s: the folder for result save, default current work directory'

def ReadFASTAFile(inputFile):
	f = open(inputFile, 'r')    # open the file
    	sequence = f.readlines()    # read the text
    	f.close()    # close it
    	# removing the trailing "\n" and any header lines
    	sequence = [line.strip() for line in sequence if not '>' in line]
    	sequence = ''.join( sequence )    # combine into a single sequence
	return sequence

def GetAngles(pose):
        phis = np.array([ pose.phi(i) for i in range(1, pose.total_residue() + 1 ) ])
        psis = np.array([ pose.psi(i) for i in range(1, pose.total_residue() + 1 ) ])
        return phis, psis

def SetAngles(pose, phis, psis):
        for i, phi, psi in zip(range(1, pose.total_residue() + 1), phis, psis):
                pose.set_phi(i, phi)
                pose.set_psi(i, psi)
## angle is an array and each element is degree of an angle instead of radian
def CorrectAngles(angles):
        temp = angles % 360
        np.putmask(temp, temp>180, temp-360)
        return temp

## angles is an array and each element is degree but not radian
## perturb angles by adding a noise sampled from normal distribution N(0, sigma)
def PerturbAngles(angles, sigma):
        noise = np.random.normal(0, sigma, angles.shape).astype(np.float32)
        return CorrectAngles( angles + noise )
	

def InitializePose(inputFile):
	if not inputFile.endswith('.pdb'):
		print 'ERROR: the input file shall be a PDB file: ', inputFile
		exit(1)
	pose = pose_from_pdb(inputFile)
	return pose

def RemoveClash(scorefxn, mover, pose):
    	for _ in range(0, 5):
        	if float(scorefxn(pose)) < 10:
            		break
        	mover.apply(pose)

def RemoveClashes(pose, flexibleRegions, ncycles=1000, tolerance=0.0001):
	assert pose is not None

	mmap = MoveMap()
	mmap.set_bb(False)
	mmap.set_chi(False)
	mmap.set_jump(False)
	for region in flexibleRegions:
		start, end = region
		for i in range(start, end+1):
			mmap.set_bb(i, True)
			mmap.set_chi(i, True)
	mmap.show()

	scriptdir = os.path.dirname(os.path.realpath(__file__))

    	sf_vdw = ScoreFunction()
    	sf_vdw.add_weights_from_file(scriptdir + '/params/scorefxn_vdw.wts')

    	min_mover_vdw = MinMover(mmap, sf_vdw, 'lbfgs_armijo_nonmonotone', tolerance, True)
    	min_mover_vdw.max_iter(ncycles)

	sf_vdw.show(pose)

	for i in range(10):
		RemoveClash(sf_vdw, min_mover_vdw, pose)
		sf_vdw.show(pose)

	switch = SwitchResidueTypeSetMover("fa_standard")
        switch.apply(pose)

	return pose

def ParseFlexibleRegions(regionStr):

	flexibleRegions = []
	fields = regionStr.split(',')
	for f in fields:
		positions = f.split('-')
		assert len(positions) == 2
		start = np.int32(positions[0])
		end = np.int32(positions[1])
		flexibleRegions.append((start, end))

	return flexibleRegions

def main(argv):

	if len(argv) < 2:
		Usage()
		exit(1)

	inputFile = argv[0]
	assert inputFile.endswith('.pdb') 
	if not os.path.isfile(inputFile):
		print 'ERROR: invalid input file for clash remove', inputFile
		exit(1)
	
	flexibleRegions = ParseFlexibleRegions(argv[1])

	try:
                opts, args = getopt.getopt(argv[2:],"n:s:",["ncycles=", "savefolder="])
                #print opts, args
        except getopt.GetoptError:
                Usage()
                exit(1)

	ncycles = 1000
	savefolder = os.getcwd()
        for opt, arg in opts:

		if opt in ("-n", "--ncycles"):
			ncycles = np.int32(arg)

		elif opt in ("-s", "--savefolder"):
			savefolder = arg

                else:
                        Usage()
                        exit(1)

	filename = os.path.basename(inputFile).split('.')[0]

	init('-hb_cen_soft -relax:default_repeats 5 -default_max_cycles 200 -out:level 300')
	rosetta.basic.options.set_boolean_option( 'run:nblist_autoupdate', True )

	pose = InitializePose(inputFile)
	if pose is None:
		print 'ERROR: the intial pose is None'
		exit(1)

	switch = SwitchResidueTypeSetMover("centroid")
        switch.apply(pose)

	pose = RemoveClashes(pose, flexibleRegions, ncycles=ncycles)
	if pose is None:
		print 'ERROR: the resultant pose is None'
		exit(1)

	savefile = filename + '.noclash.pdb'
	modelFile = os.path.join(savefolder, savefile)
	print 'Writing the noclash model to ', modelFile
	pose.dump_pdb(modelFile)


if __name__ == "__main__":
        main(sys.argv[1:])

