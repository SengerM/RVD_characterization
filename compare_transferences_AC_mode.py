import numpy as np
import nicenquickplotlib as nq
import uncertainties as unc

MEASUREMENTS_TO_COMPARE = [
	# ~ '../RVD_measurements/AC_mode/20190103112716474009',
	'../RVD_measurements/AC_mode/20190103114910874635',
	'../RVD_measurements/AC_mode/20190103130458050521',
	]
LABELS = [
	# ~ '190103A',
	'190103B',
	'190103C',
	]

freqs = []
ratios = []
for k in range(len(MEASUREMENTS_TO_COMPARE)):
	current_timestamp = MEASUREMENTS_TO_COMPARE[k]
	current_timestamp = current_timestamp[current_timestamp.rfind('/')+1:]
	data = np.genfromtxt(MEASUREMENTS_TO_COMPARE[k] + '/' + current_timestamp + '_' + 'transference_dataset1.csv')
	data = data.transpose()
	freqs.append(data[0])
	ratios.append(unc.unumpy.uarray(data[1], data[2]))

nq.plot(freqs, ratios, 
	xscale = 'L', 
	marker = '.', 
	legend = LABELS, 
	xlabel = 'Frequency (Hz)', 
	ylabel = 'Ratio',
	title = 'AC mode trensferences comparison')
nq.save_all()
nq.show()
