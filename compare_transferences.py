import numpy as np
import nicenquickplotlib as nq
import uncertainties as unc

import directories as DIRS

MEASUREMENTS_TO_COMPARE = [
	'../RVD_measurements/181219',
	'../RVD_measurements/181220A',
	'current_measurement'
	]
LABELS = [
	'181219',
	'181220A',
	'Current'
	]

freqs = []
ratios = []
phases = []
for k in range(len(MEASUREMENTS_TO_COMPARE)):
	data = np.genfromtxt(MEASUREMENTS_TO_COMPARE[k] + '/' + DIRS.TRANSFERENCE_RESULTS_DIR + '/' + 'transference_dataset1.csv')
	data = data.transpose()
	freqs.append(data[0])
	ratios.append(unc.unumpy.uarray(data[1], data[2]))
	data = np.genfromtxt(MEASUREMENTS_TO_COMPARE[k] + '/' + DIRS.TRANSFERENCE_RESULTS_DIR + '/' + 'transference_dataset2.csv')
	data = data.transpose()
	phases.append(unc.unumpy.uarray(data[1], data[2]))

nq.plot(freqs, ratios, xscale='L', marker='.', legend=LABELS, xlabel='Frequency (Hz)', ylabel='Ratio')
nq.plot(freqs, phases, xscale='L', marker='.', legend=LABELS, xlabel='Frequency (Hz)', ylabel='Phase (rad)')
nq.save_all()
nq.show()
