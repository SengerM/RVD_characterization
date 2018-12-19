import visa
import numpy as np
import time as tm
import uncertainties as unc
import uncertainties.umath
from uncertainties import unumpy as unp
import nicenquickplotlib as nq # https://github.com/SengerM/nicenquickplotlib

import lib.HP3458A as HP3458A
import lib.fitmodel as fitmodel

# Script parameters ----------------------------------------------------
RESET_INSTRUMENTS = True
SAVE_DATA = True
# MEASURING PARAMS -----------------------------------------------------
GENERATOR_FREQUENCY = 237 # Hertz.
SAMPLING_FREQUENCY = 20000 # Hertz.
SAMPLES_PER_BURST = 1000 # Number of samples to be recorded.
GENERATOR_AMPLITUDE = 1 # Peak voltage.
N_BURSTS = 1 # See note below.
DIVIDER_RATIO = 7.4/10
# Note on N_BURSTS:
	# This is a "cavernicol" way to overcome a problem regarding with 
	# the fact that the first "N" bursts taken by the voltmeteres are 
	# wrong, with "N" typically 1 or 2. I found no way to fix this 
	# problem so I decided to take N_BURSTS>2 and discard all exept the
	# last one.
# ----------------------------------------------------------------------


def measure_burst(FunGen=None, DMM=None, generator_frequency=100, generator_amplitude=1, generator_offset=0, sampling_frequency=1000, number_of_samples=1000, RVD_ratio=1, N_bursts=1, verbose=False):
	""" This function assumes that FunGen is a HP 3245A and DMM is a list
	containing two HP 3458A. The function configures the instruments and 
	return the results of the measurement. 
	
	Note on the parameter N_bursts:
		This is a "cavernicol" way to overcome a problem regarding with the fact
		that the first "N" bursts taken by the voltmeteres are wrong, with "N" 
		typically 1 or 2. I found no way to fix this problem so I decided to take 
		N_BURSTS>2 and discard all exept the last one."""
	# Configure function generator ------------
	if verbose:
		print('Setting generator output to:\n\tWaveform: sine\n\tAmplitude: ' + str(generator_amplitude) + ' V (peak voltage)\n\tOffset: ' + str(generator_offset) +'\n\tFrequency: ' + str(generator_frequency) + ' Hz')
	FunGen.write('SYNCOUT OFF') # Sync signal is output only from sync terminal in front panel.
	FunGen.write('USE CHANA') # Select channel A to receive subsequent commands.
	FunGen.write('TERM OFF') # Disconnect the output from all terminals.
	FunGen.write('IMP 0') # Select 0 Ohm output impedance mode.
	FunGen.write('ARANGE ON') # Enable autorange.
	FunGen.write('APPLY ACV ' + str(generator_amplitude*2)) # Apply sine output with specified amplitude.
	FunGen.write('FREQ ' + str(generator_frequency))
	FunGen.write('DCOFF ' + str(generator_offset)) # Generator offset.
	FunGen.write('TERM FRONT') # Connect the output to the front panel terminal (i.e. enable output).
	# Configure trigger generator --------------------------------------
	FunGen.write('USE CHANB') # Select channel B to receive subsequent commands.
	FunGen.write('TERM OFF') # Disconnect the output from all terminals.
	FunGen.write('ARANGE ON') # Enable autorange.
	FunGen.write('APPLY ACV 1')
	FunGen.write('FREQ ' + str(sampling_frequency))
	FunGen.write('TERM FRONT') # Connect the output to the front panel terminal (i.e. enable output).
	FunGen.write('PHSYNC') # Synchronize channels.
	# Launch measurements ----------------------------------------------
	FunGen.write('USE CHANB') # Select channel B to receive subsequent commands.
	FunGen.write('SYNCOUT TB0') # Route SYNC signal to TB0 port in the rear panel. This signal is the one that generates the "sample event" for the voltmeters.
	# Configure DMM ----------------------------------------------------
	if verbose:
		print('Configuring DMMs...')
	for k in range(len(DMM)):
		DMM[k].write('PRESET DIG')
		DMM[k].write('TARM HOLD')
		if k == 0: # Input signal DMM.
			DMM[k].write('DSDC ' + str(np.abs(generator_amplitude+generator_offset)))
		elif k == 1: # Output signal DMM.
			DMM[k].write('DSDC ' + str(np.abs((generator_amplitude+generator_offset)*RVD_ratio)))
		DMM[k].write('MEM LIFO') # ENABLE READING MEMORY.
		DMM[k].write('MFORMAT SINT')
		DMM[k].write('OFORMAT SINT') # Set the output format when reading the samples in memory.
		DMM[k].write('NRDGS ' + str(number_of_samples) + ', 2') # '2' means 'EXTSYN'.
		DMM[k].write('TRIG LEVEL')
		DMM[k].write('SLOPE POS')
		DMM[k].write('LEVEL 0')
		DMM[k].write('TARM AUTO')
	tm.sleep(3/generator_frequency) # This is in order to ensure the TRIG event or each voltmeter has already occured.
	time_per_burst = number_of_samples/sampling_frequency
	if verbose:
		print('Measuring... ({:.2g}'.format(time_per_burst*N_BURSTS) + ' seconds)')
	tm.sleep(time_per_burst*N_bursts) # Wait untill all burst have been taken.
	if verbose:
		print('Finishing measurements...')
	for k in range(len(DMM)):
		if verbose:
			print('Finishing voltmenter ' + str(k+1) + '... (this should not elapse more than ' + str(int(time_per_burst)) + ' seconds)')
		DMM[k].timeout = None
		DMM[k].write('TARM HOLD') # Disable triggering
		DMM[k].timeout = 5e3
		if verbose:
			print('Voltmenter ' + str(k+1) + ' finished')
	# Read samples ----------------------------
	samples = [None]*len(DMM)
	for k in range(len(DMM)):
		if verbose:
			print('Reading ' + str(number_of_samples) + ' (of ' + str(DMM[k].query('MCOUNT?')) + ') samples from voltmeter ' + str(k+1))
		samples[k] = HP3458A.read_binary_mem(DMM[k], number_of_samples)
		uncertainty = HP3458A.get_uncertainty(DMM[k])
		samples[k] = unp.uarray(samples[k], [s*uncertainty[0]+uncertainty[1] for s in np.abs(samples[k])])
	return samples


# Open instruments -----------------------------------------------------
print('Opening instruments...')
rm = visa.ResourceManager()
DMM = [None]*2
DMM[0] = rm.open_resource('GPIB0::21::INSTR') # HP3458A multimeter. High voltage side DMM.
DMM[1] = rm.open_resource('GPIB0::22::INSTR') # HP3458A multimeter. Low voltage side DMM.
FunGen = rm.open_resource('GPIB0::9::INSTR') # HP3254A universal source.
if RESET_INSTRUMENTS is True:
	for k in range(len(DMM)):
		DMM[k].write('RESET')
	FunGen.write('RESET')
	print('Instruments have been reset.')
for k in range(len(DMM)):
	DMM[k].read_termination = HP3458A.read_termination
FunGen.read_termination = HP3458A.read_termination
# Measure --------------------------------------------------------------
samples = measure_burst(FunGen=FunGen, DMM=DMM, generator_frequency=GENERATOR_FREQUENCY, generator_amplitude=GENERATOR_AMPLITUDE, sampling_frequency=SAMPLING_FREQUENCY, number_of_samples=SAMPLES_PER_BURST, verbose=True)
# Close instruments ----------------------------------------------------
print('Closing instruments...')
for k in range(len(DMM)):
	DMM[k].write('DISP OFF, \'I am DMM[' + str(k) + ']\'')
	DMM[k].close()
FunGen.write('USE CHANA') # Select channel A to receive subsequent commands.
FunGen.write('TERM OFF') # Disconnect the output from all terminals.
FunGen.write('USE CHANB') # Select channel B to receive subsequent commands.
FunGen.write('TERM OFF') # Disconnect the output from all terminals.
FunGen.close()
print('Processing data...')
# Process data ---------------------------------------------------------
def discrete_time_modeling_function(n, p):
	Vp = p[0]
	phi = p[1]
	Vos = p[2]
	return Vp*unp.sin(2*np.pi*GENERATOR_FREQUENCY/SAMPLING_FREQUENCY*n + phi) + Vos
discrete_time_model = [None]*len(samples)
for k in range(len(samples)):
	discrete_time_model[k] = fitmodel.fitmodel(discrete_time_modeling_function, r'$V_p \sin \left(\frac{\omega}{f_s} n + \phi \right) + V_{os}$', [r'$V_p$', r'$\phi$', r'$V_{os}$', ], 'discrete time fit ' + str(k+1))
	discrete_time_model[k].set_data(np.arange(len(samples[k])), samples[k])
	discrete_time_model[k].fit([GENERATOR_AMPLITUDE, 0, 0])
	discrete_time_model[k].plot_model_vs_data(xlabel='Sample number', ylabel='Voltage')
	discrete_time_model[k].plot_residuals(xlabel='Sample number', ylabel='Voltage')

nq.plot(samples, legend=['samples 1', 'samples 2'], xlabel='Sample number', ylabel='Voltage (V)')

nq.save_all(timestamp=True, csv=True)
nq.show()
