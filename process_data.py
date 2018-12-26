import uncertainties as unc
from uncertainties import unumpy as unp
import numpy as np
import os
import nicenquickplotlib as nq # https://github.com/SengerM/nicenquickplotlib

import utils.fitmodel as fitmodel
import utils.lock_in_process
import directories as DIRS
import utils.my_uncertainties_utils as munc

# -----------------------------------------
if not os.path.isdir(DIRS.UNPROCESSED_DATA_PATH):
	print('No data to be analized.')
	exit()
if len(os.listdir(DIRS.UNPROCESSED_DATA_PATH)) == 0:
	print('No data to be analized.')
	exit()
current_timestamp = os.listdir(DIRS.UNPROCESSED_DATA_PATH)[0] # This is the file to be analyzed.
current_timestamp = current_timestamp[:current_timestamp.find('_')]
print('Moving timestamp "' + current_timestamp + '" to "' + DIRS.CURRENTLY_PROCESSING_DATA_PATH + '"')
os.rename(DIRS.UNPROCESSED_DATA_PATH + current_timestamp + DIRS.CONFIG_FILE_SUFFIX, DIRS.CURRENTLY_PROCESSING_DATA_PATH + current_timestamp + DIRS.CONFIG_FILE_SUFFIX)
os.rename(DIRS.UNPROCESSED_DATA_PATH + current_timestamp + DIRS.SAMPLES_FILE_SUFFIX, DIRS.CURRENTLY_PROCESSING_DATA_PATH + current_timestamp + DIRS.SAMPLES_FILE_SUFFIX)
# Read data -------------------------------
print('Processing file with timestamp ' + current_timestamp)
samples = np.genfromtxt(DIRS.CURRENTLY_PROCESSING_DATA_PATH + current_timestamp + DIRS.SAMPLES_FILE_SUFFIX, skip_header=1)
samples = np.transpose(samples)
generator_frequency = np.genfromtxt(DIRS.CURRENTLY_PROCESSING_DATA_PATH + current_timestamp + DIRS.CONFIG_FILE_SUFFIX, skip_header=1)[0]
sampling_frequency = np.genfromtxt(DIRS.CURRENTLY_PROCESSING_DATA_PATH + current_timestamp + DIRS.CONFIG_FILE_SUFFIX, skip_header=1)[1]
generator_amplitude = np.genfromtxt(DIRS.CURRENTLY_PROCESSING_DATA_PATH + current_timestamp + DIRS.CONFIG_FILE_SUFFIX, skip_header=1)[2]
# Discrete time signal model -------------
def discrete_time_modeling_function(n, p):
	Vp = p[0]
	phi = p[1]
	Vos = p[2]
	return Vp*unp.sin(2*np.pi*generator_frequency/sampling_frequency*n + phi) + Vos
discrete_time_model = [None]*2
for k in range(2):
	discrete_time_model[k] = fitmodel.fitmodel(discrete_time_modeling_function, r'$V_p \sin \left(\frac{\omega}{f_s} n + \phi \right) + V_{os}$', [r'$V_p$', r'$\phi$', r'$V_{os}$', ], 'DT' + str(k+1))
	discrete_time_model[k].set_data(np.arange(len(samples[k])), samples[k])
	discrete_time_model[k].fit([generator_amplitude, 0, 0])
# PLOT ------------------------------------
for k in range(2):
	fig = discrete_time_model[k].plot_model_vs_data(xlabel='Sample number', ylabel='Voltage (V)', nicebox=True, marker='.')
	fig.axes[-1].set_xlim([0, 10*sampling_frequency/2/np.pi/generator_frequency])
# Transference calculation ---------------
T_abs = np.abs(discrete_time_model[1].param_val(0)/discrete_time_model[0].param_val(0)) # The "abs" is because sometimes the fitting process converges to a negative amplitude.
T_phi = utils.lock_in_process.lock_in_process(samples[0], samples[1])
# Save data ------------------------------
os.rename(DIRS.CURRENTLY_PROCESSING_DATA_PATH + current_timestamp + DIRS.CONFIG_FILE_SUFFIX, DIRS.PROCESSED_DATA_PATH + current_timestamp + DIRS.CONFIG_FILE_SUFFIX)
os.rename(DIRS.CURRENTLY_PROCESSING_DATA_PATH + current_timestamp + DIRS.SAMPLES_FILE_SUFFIX, DIRS.PROCESSED_DATA_PATH + current_timestamp + DIRS.SAMPLES_FILE_SUFFIX)
nq.save_all(mkdir=DIRS.PROCESSED_DATA_PATH + current_timestamp + 'plots')
with open(DIRS.PROCESSED_DATA_PATH + current_timestamp + DIRS.TRANSFERENCE_FILE_SUFFIX, 'w') as ofile:
	print('T_abs.n\tT_abs.s\tT_phi.n', file=ofile)
	print(str(T_abs.n) + '\t' + str(T_abs.s) + '\t' + str(T_phi), file=ofile)
print('Analysis completed.')
print('Original data and results can be found in "' + DIRS.PROCESSED_DATA_PATH + '"')
