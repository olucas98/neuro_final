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
			fields = line.split('')
			print(fields)
	break
		