import numpy as np
from scipy import fftpack

def lock_in_process(S1, S2):
	if len(S1) != len(S2):
		raise ValueError('Data sets lengths mismatch!')
	if len(S1) < 100:
		raise ValueError('Miminum number of points is 100')
	S1 = np.array(S1)
	S2 = np.array(S2)
	Squad = fftpack.hilbert(S1) # Quadrature signal
	Sdf = np.dot(S1, S2)
	Sdc = np.dot(Squad, S2)
	phi = np.arctan(Sdc/Sdf)
	return phi
