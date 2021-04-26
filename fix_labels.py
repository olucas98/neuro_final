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
		for line in lines:
			fields = line.split()
			print(fields)
			field[1] = np.clip(field[1], 0, 1)
			field[2] = np.clip(field[2], 0, 1)
			print(fields)
	break
		