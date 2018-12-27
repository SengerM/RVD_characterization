import os
import numpy as np
import nicenquickplotlib as nq

import directories as DIRS

def shift_and_std(a, b):
	a,b = shift_arrays(a,b)
	return (a-b).std()

def shift_arrays(a, b):
	"""
	a,b --> one dimension arrays
	'a' is shifted left and 'b' is shifted right.
	"""
	a = a[:-1]
	b = b[1:]
	return a, b

# ----------------------------------------------------------------------
if not os.path.isdir(DIRS.UNPROCESSED_DATA_PATH):
	print('No data to be fixed.')
	exit()
if len(os.listdir(DIRS.UNPROCESSED_DATA_PATH)) == 0:
	print('No data to be fixed.')
	exit()
current_timestamp = os.listdir(DIRS.UNPROCESSED_DATA_PATH)[0] # This is the file to be fixed.
current_timestamp = current_timestamp[:current_timestamp.find('_')]
# Read data -------------------------------
print('Fixing trigger problem for file with timestamp ' + current_timestamp)
samples = np.genfromtxt(DIRS.UNPROCESSED_DATA_PATH + current_timestamp + DIRS.SAMPLES_FILE_SUFFIX, skip_header=1)
samples = np.transpose(samples)

temp = [None]*len(samples)
for k in range(len(samples)):
	temp[k] = np.array(samples[k])
samples = temp
for k in range(len(temp)):
	temp[k] = temp[k]/temp[k].max()

previous_std = (temp[0] - temp[1]).std()
while True:
	if previous_std > shift_and_std(temp[0], temp[1]):
		temp[0], temp[1] = shift_arrays(temp[0], temp[1])
		previous_std = (temp[0] - temp[1]).std()
		samples[0], samples[1] = shift_arrays(samples[0], samples[1])
	elif previous_std > shift_and_std(temp[1], temp[0]):
		temp[1], temp[0] = shift_arrays(temp[1], temp[0])
		previous_std = (temp[1] - temp[0]).std()
		samples[1], samples[0] = shift_arrays(samples[1], samples[0])
	else:
		break

with open(DIRS.TRIGGER_PROBLEM_FIXED_DATA_PATH + current_timestamp + DIRS.SAMPLES_FILE_SUFFIX, 'w') as ofile:
	print('Samples1 (V)\tSamples2 (V)', file=ofile)
	for k in range(len(samples[0])):
		print(str(samples[0][k]) + '\t' + str(samples[1][k]), file=ofile)
os.rename(DIRS.UNPROCESSED_DATA_PATH + current_timestamp + DIRS.CONFIG_FILE_SUFFIX, DIRS.TRIGGER_PROBLEM_FIXED_DATA_PATH + current_timestamp + DIRS.CONFIG_FILE_SUFFIX)
os.remove(DIRS.UNPROCESSED_DATA_PATH + current_timestamp + DIRS.SAMPLES_FILE_SUFFIX)
