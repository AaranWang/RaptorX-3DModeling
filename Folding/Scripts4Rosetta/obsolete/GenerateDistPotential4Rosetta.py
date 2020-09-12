import os
import sys

import cPickle

import numpy as np
import scipy
from scipy.optimize import curve_fit

import getopt

import DL4DistancePrediction3.config
from DL4DistancePrediction3.config import  Response2LabelName, Response2LabelType, SelectAtomPair

from LogNormalFit import OneLogNormal

def Usage():
	print 'python GenerateDistPotential4Rosetta.py [-f funcType] [-a atomPairType] [-s minSeqSep] [ -c potentialCutoff ] [ -b barrier] [-D maxDist ] [ -E enhanced_cutoff ] potential_PKL'
	print '     potential_PKL: the raw potential matrix in PKL format. It is a tuple of 4 items: target, sequence, potential (dict) and distCutoffs (dict)'
	print '     -f: potential function type: SPLINE(default), LOGNORMAL, LNSPLINE, LNSPLINE2 and ETABLE (obsolete)'
	print '		LOGNORMAL: use lognormal to fit the potential generated by deep learning and then generated parameters for LOGNORMAL'
	print '			currently Rosetta does not support LOGNORMAL, we may have to revise the Rosetta C++ code'	
	print '		LNSPLINE: use lognormal to fit the potential and generate potential values for distance<4 or >20, then use the original potential for distance between 4 and 20'
	print '		LNSPLINE2: use lognormal to fit the potential and generate potential values for all distance and use them for SPLINE'
	print '     -a: atom pair type, e.g., All, CbCb (default), CaCa, CaCa+CbCb where All indicates 5 atom pair types'
	print '     -s: output potential for atom pairs with sequence separation at least this value, default 3'
	print '     -c: when the best (lowest) potential of one atom pair is larger (worse) than this value (default 20), ignore this atom pair. '
	print '     -b: the energy barrier for atom pairs with a small distance, default 0.5. Not used when funcType is LOGNORMAL, LNSPLINE and LNSPLINE2'
	print '     -D: the maximum valid distance for distance-based potential, default 20'
	print '     -E: only valid when the specified value is <-1.5 (default invalid). When the best potential of an atom pair <= this value, enhance Spline potential with a bounded function which is 0 for distance<20 and positive otherwise'

def Compatible(response, apts):
	for apt in apts:
		if response.startswith(apt):
			return True, apt
	return False, None

def GenerateLogNormalPotential(target, sequence, potential, distCutoffs, apts=['CbCb'], minSeqSep=3, potThreshold=20., funcType='LOGNORMAL', LastX=22):

	## this folder save the histogram file for each atom pair
	histfileDir = funcType + 'Potential4' + target + '-' + str(minSeqSep) + '-' + str(potThreshold) + '-' + str(LastX) + '/'
	if not os.path.isdir(histfileDir):
		os.mkdir(histfileDir)

	expVal = 0.
	weight = 1.
        binWidth = 0.5
	xk2 = np.arange(0, LastX + binWidth, binWidth).tolist()
	xk = [ x0 - binWidth/2 for x0 in xk2 ]

	potentialFileSuffix= '.' + funcType + '.txt'
	rosettaPotentialFileName = target + '.distPotential4Rosetta' + '.s' + str(minSeqSep) + '.c'+ str(potThreshold) + '.D' + str(LastX) + potentialFileSuffix
        fh_rosetta = open(rosettaPotentialFileName, 'w')

        for apt, pot in potential.iteritems():

		description = apt
		#print 'response=', response

                #apt = Response2LabelName(response)
                #distLabelType = Response2LabelType(response)
                #subtype = distLabelType[len('Discrete'):]
                #assert subtype == '25C'

		flag, atomType = Compatible(apt, apts)
		if not flag:
			continue

                x = distCutoffs[apt][1:]
		x = [ x0 - binWidth/2 for x0 in x ]

                size = pot.shape
                for i in xrange(size[0]):
                        potStrs = []

                        for j in xrange(i+ minSeqSep, size[1]):
                                y = pot[i, j]
				## if the best potential is too big, then skip
				ymin = min(y[:-1])
				if (ymin > potThreshold):
					continue

                                atom1, atom2 = SelectAtomPair(sequence, i, j, atomType)

				## fit potential by a log normal function
				params, pcov = curve_fit(OneLogNormal, x, y[: -1], method='trf', bounds=([np.log(4.0), 0.01, 0, 0], [np.inf, np.inf, 20, 10]), maxfev=20000)

				if funcType == 'LOGNORMAL':
					## We assume that Rosetta uses the format "LOGNORMAL mean deviation scale offset"
                                	potStr = ' '.join(['AtomPair', atom1.upper(), str(i+1), atom2.upper(), str(j+1), 'LOGNORMAL'] + [ "{:.4f}".format(e) for e in params ] )
                                	potStrs.append(potStr)
					continue
				
				"""	
				yk_1 = OneLogNormal(xk[1:], *params)
				print len(yk_1)
				yk_0 = OneLogNormal(0, *params)
				## use linear interpolation to estimate the value of y when x = -binWidth/2
				yk_new =  [ 2*yk_0 - yk_1[0] ]
				yk_new.extend(yk_1)
				"""

				yk_new = OneLogNormal(xk[1:], *params).tolist()
				yk_0 = OneLogNormal(0, *params)
				yk_new.insert(0, 2*yk_0 - yk_new[0] )

				#print len(xk), len(yk_new), yk_new[0], yk_0

				if funcType == 'LNSPLINE':	
					yk = []
					## replace some potentials in yk by original value
					for x0, y0 in zip(xk, yk_new):
						if x0>=x[0] and x0<=x[-1]:
							index = np.int32( (x0-x[0])/binWidth )
							yk.append( y[index] )
						else:
							yk.append( y0 )
				else:
					yk = yk_new

				#print len(yk)

				histfile = os.path.join(histfileDir, 'R' + str(i+1) + atom1.upper() + '-' + 'R' + str(j+1) + atom2.upper() + '.potential.txt')
				xStr = '\t'.join(['x_axis'] + [ "{:.4f}".format(e) for e in xk ] )
				yStr = '\t'.join(['y_axis'] + [ "{:.4f}".format(e) for e in yk ] )
				## write histogram to histfile
				fh = open(histfile, 'w')
				fh.write('\n'.join([xStr, yStr]) + '\n')
				fh.close()

				##Rosetta uses the format "SPLINE description histogram_file_path experimental_value weight bin_size"
                                potStr = ' '.join(['AtomPair', atom1.upper(), str(i+1), atom2.upper(), str(j+1), 'SPLINE', description, histfile] + [ "{:.4f}".format(e) for e in [expVal, weight, binWidth] ] )
                                potStrs.append(potStr)


                        if len(potStrs) >0:
                                fh_rosetta.write('\n'.join(potStrs) + '\n')

def GenerateSplinePotential(target, sequence, potential, distCutoffs, apts=['CbCb'], minSeqSep=3, potThreshold=20., barrier=3, LastX=22, enhanced=1000):

	## this folder save the histogram file for each atom pair
	if enhanced >= -0.5 :
		histfileDir = 'SplinePotential4' + target + '.s' + str(minSeqSep) + '.b' + str(barrier) + '.c' + str(potThreshold) + '.D' + str(LastX) + '/'
	else:
		histfileDir = 'SplinePotential4' + target + '.s' + str(minSeqSep) + '.b' + str(barrier) + '.c' + str(potThreshold) + '.D' + str(LastX) + '.E' + str(-enhanced) + '/'

	if not os.path.isdir(histfileDir):
		os.mkdir(histfileDir)

	expVal = 0.
	weight = 1.

	potentialFileSuffix='.SPLINE.txt'
	if enhanced >= -0.5:
		rosettaPotentialFileName = target + '.distPotential4Rosetta' + '.s' + str(minSeqSep) + '.b'+ str(barrier) + '.c' + str(potThreshold) + '.D' + str(LastX) + potentialFileSuffix
	else:
		rosettaPotentialFileName = target + '.distPotential4Rosetta' + '.s' + str(minSeqSep) + '.b'+ str(barrier) + '.c' + str(potThreshold) + '.D' + str(LastX) + '.E' + str(-enhanced) + potentialFileSuffix

        fh_rosetta = open(rosettaPotentialFileName, 'w')

        for apt, pot in potential.iteritems():

		description = apt
		#print 'response=', response

                #apt = Response2LabelName(response)
                #distLabelType = Response2LabelType(response)
                #subtype = distLabelType[len('Discrete'):]
                #assert subtype == '25C'

		flag, atomType = Compatible(apt, apts)
		if not flag:
			continue

                x = distCutoffs[apt][1:]
                binWidth = 0.5

                xPrefix = np.arange(-binWidth, x[0], binWidth).tolist()
		yPrefix = np.arange( (len(xPrefix)-1) * barrier, -barrier, -barrier).tolist()

		#xSuffix = np.arange(x[-1] + 0.5, LastX+0.5, binWidth).tolist()
		xSuffix = np.arange(x[-1], LastX+binWidth, binWidth).tolist()
		ySuffix = [ 0.0 ] * len(xSuffix)

                xk = sum([xPrefix, x[:-1].tolist(), xSuffix], [])
		xk = [ xe + binWidth/2. for xe in xk ]
                xk2 = xk[0 : len(xk) - len(xSuffix) ]
                #print xk


                size = pot.shape
                for i in xrange(size[0]):
                        potStrs = []

                        for j in xrange(i+ minSeqSep, size[1]):
                                y = pot[i, j]
				## if the best potential is too big, then skip
				ymin = min(y[:-1])
				ymin_idx = np.argmin(y[:-1])
				if (ymin > potThreshold):
					continue

				yPrefix2 = [ y[0] + y0 for y0 in yPrefix ]
				yk2 = yPrefix2 + y[1:-1].tolist()
				yk = yk2 + ySuffix
                                #print yk
                                assert len(xk) == len(yk)

                                atom1, atom2 = SelectAtomPair(sequence, i, j, atomType)
				histfile = os.path.join(histfileDir, 'R' + str(i+1) + atom1.upper() + '-' + 'R' + str(j+1) + atom2.upper() + '.potential.txt')

				if  enhanced >= -1.5 or ymin > enhanced or ymin_idx >= (15.5-x[0])/binWidth :
					xStr = '\t'.join(['x_axis'] + [ "{:.4f}".format(e) for e in xk ] )
					yStr = '\t'.join(['y_axis'] + [ "{:.4f}".format(e) for e in yk ] )

					##Rosetta uses the format "SPLINE description histogram_file_path experimental_value weight bin_size"
                                	potStr = ' '.join(['AtomPair', atom1.upper(), str(i+1), atom2.upper(), str(j+1), 'SPLINE', description, histfile] + [ "{:.4f}".format(e) for e in [expVal, weight, binWidth] ] )
				else:
					xStr = '\t'.join(['x_axis'] + [ "{:.4f}".format(e) for e in xk2 ] )
					yStr = '\t'.join(['y_axis'] + [ "{:.4f}".format(e - yk2[-1]) for e in yk2 ] )

                                	part1=['AtomPair', atom1.upper(), str(i+1), atom2.upper(), str(j+1), 'SUMFUNC', '3']
					part2=['CONSTANTFUNC', "{:.4f}".format(yk2[-1]) ]
					#part3=['BOUNDED', '0', "{:.1f}".format(xk2[-1] - binWidth/2.), "{:.4f}".format(5./abs(ymin)), 'test']
					part3=['BOUNDED', '0', "{:.2f}".format(xk2[-1]), "{:.4f}".format(10./abs(ymin)), 'test']
					part4=['SPLINE', description, histfile] + [ "{:.4f}".format(e) for e in [expVal, weight, binWidth] ]
                                	potStr = ' '.join( part1 + part2 + part3 + part4 )

				## write histogram to histfile
				fh = open(histfile, 'w')
				fh.write('\n'.join([xStr, yStr]) + '\n')
				fh.close()

                                potStrs.append(potStr)


                        if len(potStrs) >0:
                                fh_rosetta.write('\n'.join(potStrs) + '\n')


def GenerateEtablePotential(target, sequence, potential, distCutoffs, apts=['CbCb'], minSeqSep=3, potThreshold=20., barrier=4.0, LastX=22):
	potentialFileSuffix='.ETable.txt'
	rosettaPotentialFileName = target + '.distPotential4Rosetta' + '.s' + str(minSeqSep) + '.b'+ str(barrier) + potentialFileSuffix
        fh_rosetta = open(rosettaPotentialFileName, 'w')

        for response, pot in potential.iteritems():
                apt = Response2LabelName(response)
                distLabelType = Response2LabelType(response)
                subtype = distLabelType[len('Discrete'):]
                #assert subtype == '25C'

                if apt not in set(apts):
                        continue

                x = distCutoffs[response][1:]

                ##here we need to make sure that binWidth = 0.5
                assert x[0] == 4.0 or x[0] == 4.5
		assert x[1]-x[0] == 0.5
                binWidth = 0.5
                xPrefix = np.arange(0, x[0], binWidth).tolist()
                yPrefix = np.arange( 7*barrier, 0., -barrier).tolist()

                xmin = 0
                xmax = x[-1] + 0.5
                xSuffix = [ xmax ]
                ySuffix = [ 0.0 ]

                xk = sum([xPrefix, x.tolist(), xSuffix], [])
                #print xk

                stepSize = 0.1
                xmax2 = x[-1] + 0.2
                numBoundaries = int(round( (xmax2 - xmin)/stepSize + 1 ) )
                xnew =  np.array ( np.linspace(xmin, xmax2, num=numBoundaries).tolist()  ).astype(np.float32)
                #print numBoundaries
                #print len(xnew)
                #print xnew

                size = pot.shape
                for i in xrange(size[0]):
                        potStrs = []

                        for j in xrange(i+ minSeqSep, size[1]):
                                y = pot[i, j]
				## if the best potential is too big, then skip
				ymin = min(y[:-1])
				if (ymin > potThreshold):
					continue

                                ## energy for distance=3.5
                                if y[0] < 0:
                                        E435 = 0.
				else:
                                	E435 = (barrier + y[0])/2

                         	yPrefix2 = [E435 ] + [ y[0] ] * (len(xPrefix) - len(yPrefix) -1)
                                yk = yPrefix + yPrefix2 + y[:-1].tolist() + ySuffix
                                #print yk
                                assert len(xk) == len(yk)

                                ##here we shift xk by 0.25 to the mid point of one distance bin
                                ynew = scipy.interpolate.spline(np.array(xk)-binWidth/2, yk, xnew)
                                #print len(ynew)
                                #print ynew

                                atom1, atom2 = SelectAtomPair(sequence, i, j, apt)
                                potStr = ' '.join(['AtomPair', atom1.upper(), str(i+1), atom2.upper(), str(j+1), 'ETABLE', str(xmin), str(xmax2) ] + [ "{:.4f}".format(e) for e in ynew ] )
                                potStrs.append(potStr)

                        if len(potStrs) >0:
                                fh_rosetta.write('\n'.join(potStrs) + '\n')

        fh_rosetta.close()


def main(argv):

	inputFile = None

        apts = ['CbCb']
        minSeqSep = 3
	potCutoff = 20.
	barrier = 0.5
	LastX = 20
	enhanced = 10

	funcType = 'SPLINE'
	allFuncTypes = set(['SPLINE', 'LOGNORMAL', 'LNSPLINE', 'LNSPLINE2', 'ETABLE'])

	#print argv

	if len(argv) < 1:
		Usage()
		exit(1)

        try:
                opts, args = getopt.getopt(argv,"a:f:s:c:b:D:E:",["atomPairType=", "funcType=", "minSeqSep=", "potentialCutoff=", "barrier=", "maxDist=", "enhanced="])
                print opts, args
        except getopt.GetoptError:
                Usage()
                exit(1)

        if len(args) != 1:
                Usage()
                exit(1)


	inputFile = args[0]

        for opt, arg in opts:

                if opt in ("-a", "--atomPairType"):
                        aptStr = arg
                        if aptStr.upper() == 'All'.upper():
                                apts = config.allAtomPairTypes

	  	elif opt in ("-s", "--minSeqSep"):
                        minSeqSep = np.int32(arg)
                        if minSeqSep < 1:
                                print 'ERROR: minSeqSep shall be at least 1'
                                exit(1)

                elif opt in ("-c", "--potentialCutoff"):
                        potCutoff = np.float32(arg)

                elif opt in ("-f", "--funcType"):
                        funcType = arg.upper()
			if funcType not in allFuncTypes:
				print 'ERROR: unsupported potential func type:', funcType
				exit(1)

		elif opt in ("-b", "--barrier"):
			barrier = np.float32(arg)
			assert barrier>=0

		elif opt in ("-D", "--maxDist"):
			LastX = np.float32(arg)

		elif opt in ("-E", "--enhanced"):
			enhanced = np.float32(arg)

                else:
                        Usage()
                        exit(1)

	if inputFile is None:
                print 'Please provide an input file'
                exit(1)

        if not os.path.isfile(inputFile):
                print 'The input file does not exist: ', inputFile
                exit(1)

	assert LastX >= 20

	fh = open(inputFile, 'r')
	target, sequence, potential, distCutoffs = cPickle.load(fh)
	fh.close()

	if funcType == 'SPLINE':
		GenerateSplinePotential(target, sequence, potential, distCutoffs, minSeqSep=minSeqSep, potThreshold=potCutoff, apts=apts, barrier=barrier, LastX=LastX, enhanced=enhanced)

	elif funcType == 'ETABLE':
		GenerateETablePotential(target, sequence, potential, distCutoffs, minSeqSep=minSeqSep, potThreshold=potCutoff, apts=apts, barrier=barrier, LastX=LastX)
	else:
		GenerateLogNormalPotential(target, sequence, potential, distCutoffs, minSeqSep=minSeqSep, potThreshold=potCutoff, apts=apts, funcType=funcType, LastX=LastX)

if __name__ == "__main__":
        main(sys.argv[1:])

