import visa
import numpy as np
import time as tm
import uncertainties as unc
import uncertainties.umath
from uncertainties import unumpy as unp
import nicenquickplotlib as nq # https://github.com/SengerM/nicenquickplotlib

import utils.HP3458A as HP3458A
import utils.fitmodel as fitmodel

# Script parameters ----------------------------------------------------
RESET_INSTRUMENTS = True
# MEASURING PARAMS -----------------------------------------------------
GENERATOR_FREQUENCIES = np.logspace(np.log10(40), np.log10(100000), 2)
GENERATOR_AMPLITUDE = 10 # Peak voltage.
DIVIDER_RATIO = 1/10
N_READINGS_PER_FREQUENCY = 2
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
	tm.sleep(1)
for dmm in DMM:
	dmm.read_termination = HP3458A.read_termination
	dmm.timeout = 60e4
FunGen.read_termination = HP3458A.read_termination
# Configure instruments ------------------------------------------------
DMM[0].write('FUNC ACV,' + str(GENERATOR_AMPLITUDE))
DMM[1].write('FUNC ACV,' + str(GENERATOR_AMPLITUDE*DIVIDER_RATIO))
for dmm in DMM:
	dmm.write('SETACV SYNC')
	dmm.write('NRDGS ' + str(N_READINGS_PER_FREQUENCY))
	dmm.write('TARM HOLD')
# Measure --------------------------------------------------------------
V_in = [None]*len(GENERATOR_FREQUENCIES)
V_out = [None]*len(V_in)
V_in_buffer = [None]*N_READINGS_PER_FREQUENCY
V_out_buffer = [None]*N_READINGS_PER_FREQUENCY
for k,freq in enumerate(GENERATOR_FREQUENCIES):
	print('Measuring at ' + str(freq) + ' Hz')
	FunGen.write('USE CHANA') # Select channel A to receive subsequent commands.
	FunGen.write('TERM OFF') # Disconnect the output from all terminals.
	FunGen.write('IMP 0') # Select 0 Ohm output impedance mode.
	FunGen.write('ARANGE ON') # Enable autorange.
	FunGen.write('APPLY ACV ' + str(GENERATOR_AMPLITUDE*2)) # Apply sine output with specified amplitude.
	FunGen.write('FREQ ' + str(freq))
	FunGen.write('DCOFF 0') # Generator offset.
	for dmm in DMM:
		dmm.write('TARM HOLD')
		dmm.write('ACBAND ' + str(freq*(1-.1)) + ',' + str(freq*(1+.1)))
		dmm.write('MEM LIFO') # ENABLE READING MEMORY.
		dmm.write('MFORMAT ASCII')
		dmm.write('OFORMAT ASCII')
		dmm.write('TARM AUTO')
	tm.sleep(1)
	FunGen.write('TERM FRONT') # Connect the output to the front panel terminal (i.e. enable output).
	for j in range(N_READINGS_PER_FREQUENCY):
		V_in_buffer[j] = float(DMM[0].query('RMEM ' + str(j)))
		V_out_buffer[j] = float(DMM[1].query('RMEM ' + str(j)))
	V_in[k] = np.array(V_in_buffer)
	V_out[k] = np.array(V_out_buffer)
	print('Vin = ' + str(V_in[k]))
	print('V_out = ' + str(V_out[k]))
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
# Process data ---------------------------------------------------------
input_value = [None]*len(V_in)
output_value = [None]*len(V_in)
vin_n = [None]*len(V_in)
vin_s = [None]*len(V_in)
vout_n = [None]*len(V_in)
vout_s = [None]*len(V_in)
for k in range(len(V_in)):
	vin_n[k] = V_in[k].mean()
	vin_s[k] = V_in[k].std()
	vout_n[k] = V_out[k].mean()
	vout_s[k] = V_out[k].std()
input_value = unp.uarray(vin_n, vin_s)
output_value = unp.uarray(vout_n, vout_s)

nq.plot(
	x = GENERATOR_FREQUENCIES, 
	y = [input_value, output_value],
	together = False,
	legend = ['$V_{in}$', '$V_{out}$'],
	xlabel = 'Frequency (Hz)',
	ylabel = 'Voltage (V)',
	marker = '.',
	xscale = 'L',
	title = 'Signals')
nq.plot(
	x = GENERATOR_FREQUENCIES,
	y = [output_value/input_value, unp.std_devs(output_value/input_value)/unp.nominal_values(output_value/input_value)*1e6],
	together = False,
	xlabel = 'Frequency (Hz)',
	ylabel = ['Ratio', 'Error (ppm)'],
	marker = '.',
	xscale = 'L',
	title = 'Transference')

nq.save_all(timestamp=True, csv=True)
nq.show()
