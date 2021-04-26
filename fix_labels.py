import numpy as np
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--dir')
args = parser.parse_args()

labelfiles = os.listdir(args.dir)

for lf in labelfiles:
	with open(os.path.join(args.dir, lf), 'r') as file:
		lines = file.readlines()
		labels_out = ''
		for line in lines:
			fields = line.split()
			fields[1] = str(np.clip(float(fields[1]), 0, 1))
			fields[2] = str(np.clip(float(fields[2]), 0, 1))
			labels_out += ' '.join(fields) + '\n'
		print(labels_out)
	break
		