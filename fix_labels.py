import numpy as np
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--in_dir')
parser.add_argument('--out_dir')
args = parser.parse_args()

labelfiles = os.listdir(args.in_dir)
os.makedirs(args.out_dir, exist_ok=True)

for lf in labelfiles:
	with open(os.path.join(args.in_dir, lf), 'r') as file:
		lines = file.readlines()
		labels_out = ''
		for line in lines:
			fields = line.split()
			for i in range(1, len(fields))
				fields[i] = str(np.clip(float(fields[i]), 0, 1))
			labels_out += ' '.join(fields) + '\n'
	
	with open(os.path.join(args.out_dir, lf), 'w+') as file:
		file.write(labels_out)
		