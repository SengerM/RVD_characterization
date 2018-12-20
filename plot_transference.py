import uncertainties as unc
from uncertainties import unumpy as unp
from uncertainties.umath import *
import numpy as np
import os
import nicenquickplotlib as nq

import utils.my_uncertainties_utils as munc
import directories as DIRS

dirlist = os.listdir(DIRS.PROCESSED_DATA_PATH)
timestamps_to_analyze = []
for k_dir in dirlist:
	if k_dir[-len(DIRS.SAMPLES_FILE_SUFFIX):] == DIRS.SAMPLES_FILE_SUFFIX:
		timestamps_to_analyze.append(k_dir[:k_dir.find(DIRS.SAMPLES_FILE_SUFFIX[0])])
# Read data ------------------------------------------------------------
freq = []
Transferences_abs = []
Transferences_phi = []
for k in range(len(timestamps_to_analyze)):
	current_timestamp = timestamps_to_analyze[k]
	generator_frequency = np.genfromtxt(DIRS.PROCESSED_DATA_PATH + current_timestamp + DIRS.CONFIG_FILE_SUFFIX, skip_header=1)[0]
	current_T_abs_n = np.genfromtxt(DIRS.PROCESSED_DATA_PATH + current_timestamp + DIRS.TRANSFERENCE_FILE_SUFFIX, skip_header=1)[0]
	current_T_abs_s = np.genfromtxt(DIRS.PROCESSED_DATA_PATH + current_timestamp + DIRS.TRANSFERENCE_FILE_SUFFIX, skip_header=1)[1]
	current_T_phi_n = np.genfromtxt(DIRS.PROCESSED_DATA_PATH + current_timestamp + DIRS.TRANSFERENCE_FILE_SUFFIX, skip_header=1)[2]
	current_T_phi_s = 0 # This was not yet implemented by the "lock-in process".
	if not generator_frequency in freq:
		freq.append(generator_frequency)
		freq = sorted(freq)
	current_index = freq.index(generator_frequency) # Index position of the current frequency in the frequencies list.
	if len(freq) != len(Transferences_abs): # This means that the current 'generator_frequency' is a new value.
		Transferences_abs.insert(current_index, [])
		Transferences_phi.insert(current_index, [])
	Transferences_abs[current_index].append(unc.ufloat(current_T_abs_n, current_T_abs_s))
	Transferences_phi[current_index].append(unc.ufloat(current_T_phi_n, current_T_phi_s))
# Calculation of mean values and standard deviations for each frequency point ---
T_abs_n = unp.uarray(np.zeros(len(freq)), np.zeros(len(freq)))
T_abs_s = unp.uarray(np.zeros(len(freq)), np.zeros(len(freq)))
T_phi_n = unp.uarray(np.zeros(len(freq)), np.zeros(len(freq)))
T_phi_s = unp.uarray(np.zeros(len(freq)), np.zeros(len(freq)))
T_abs_definitive = unp.uarray(np.zeros(len(freq)), np.zeros(len(freq)))
T_phi_definitive = unp.uarray(np.zeros(len(freq)), np.zeros(len(freq)))
number_of_bursts = [None]*len(freq)
for k in range(len(freq)):
	number_of_bursts[k] = len(Transferences_abs[k])
	# Mean value calculation ---------------
	for kk in range(number_of_bursts[k]):
		T_abs_n[k] += Transferences_abs[k][kk]
		T_phi_n[k] += Transferences_phi[k][kk]
	T_abs_n[k] /= number_of_bursts[k]
	T_phi_n[k] /= number_of_bursts[k]
	# Standard deviation --------------------
	for kk in range(number_of_bursts[k]):
		T_abs_s[k] += (Transferences_abs[k][kk]-T_abs_n[k])**2
		T_phi_s[k] += (Transferences_phi[k][kk]-T_phi_n[k])**2
	if number_of_bursts[k] > 1:
		T_abs_s[k] /= number_of_bursts[k]-1
		T_phi_s[k] /= number_of_bursts[k]-1
	T_abs_s[k] = sqrt(T_abs_s[k])
	T_phi_s[k] = sqrt(T_phi_s[k])
	# Definitive values calculation ---------
	# 	In this step I keep the worst of the std's obtained either
	# 	when calculating the mean value using the std's from measurements
	# 	or the std obtained by the disperssion of the points.
	T_abs_definitive[k] = unc.ufloat(T_abs_n[k].n, T_abs_n[k].s + T_abs_s[k].n + T_abs_s[k].s)
	T_phi_definitive[k] = unc.ufloat(T_phi_n[k].n, T_phi_n[k].s + T_phi_s[k].n + T_phi_s[k].s)
freq = np.array(freq)
# PLOT ----------------------------
nq.plot(x=freq, 
	y=[T_abs_definitive, T_phi_definitive],
	together=False,
	xlabel='Frequency (Hz)',
	ylabel=['Ratio','Phase (rad)'],
	xscale='L',
	title='Transference',
	marker='.'
	)
nq.plot(x=freq, 
	y=[unp.std_devs(T_abs_definitive)/unp.nominal_values(T_abs_definitive), np.abs(unp.std_devs(T_phi_definitive)/unp.nominal_values(T_phi_definitive))],
	together=False,
	xlabel='Frequency (Hz)',
	ylabel=[r'Ratio err $\frac{\sigma}{\mu}$', r'Phase err $\frac{\sigma}{\mu}$'],
	xscale='L',
	yscale='L',
	title='Transference uncertainties',
	marker='.'
	)
nq.save_all(mkdir=DIRS.TRANSFERENCE_RESULTS_PATH, csv=True)
nq.show()
