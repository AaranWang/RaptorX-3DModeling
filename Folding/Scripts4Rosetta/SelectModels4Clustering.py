import os
import sys
import numpy as np

def Usage():
	print 'python SelectModels4Clustering.py scorefile [ranking_score]'
	print '	scorefile: this file is generated by ExtractScoreFromRelaxedModels.sh'
	print ' ranking_score: the score used to rank models from low to high score'
	print '		0: distance potential + dihedral potential + angle potential (default)'
	print '		1: distance potential '
	print '		2: dihedral potential '
	print '		3: angle potential '

def SelectModels(scorefile, rankingScore):
	with open(scorefile, 'r') as fh:
		content = [ line.strip() for line in list(fh) ]
	modelScores = []
	for row in content:
		fields = row.split()
		assert len(fields) >= 5
		modelFile = fields[0]
		scores = [ np.float32(f) for f in fields[1:] ]
		modelScores.append( [ modelFile ] + scores )

	if len(modelScores) < 1:
		return []
	maxScore = abs( min( [ ms[1+rankingScore] for ms in modelScores ] ) )

	#print "maxScore of ", scorefile, maxScore

	selectedModels = []
	for ms in modelScores:
		if ms[1+rankingScore] < maxScore:
			selectedModels.append( ms[0] )

	return selectedModels

if len(sys.argv) < 2:
	Usage()
	exit(1)

scorefile=sys.argv[1]
rankingScore = 0
if len(sys.argv) >= 3:
	rankingScore = np.int32(sys.argv[2])
	assert rankingScore in set([0, 1, 2, 3])

selected = SelectModels(scorefile, rankingScore)

## print
print '\n'.join(selected)