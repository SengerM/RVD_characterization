import uncertainties as unc
import numpy as np

def ufloat_nice_str(uf):
	# FALLA AL IMPRIMIR VALORES CERCANOS A 1, 10, 100, etc.
	"Prints the magnitude in the format v.vvvv(v+-e) being 'v' the relevant digits of the magnitude value and '+-e' the most significant digit of the error."
	if np.isnan(uf.n) or np.isnan(uf.s):
		return 'NaN'
	if uf.s == 0 or uf.n == 0:
		return str(uf.n)
	if uf.s >= np.fabs(uf.n):
		return '{:.0e} +- {:.0e}'.format(uf.n, uf.s)
	else:
		n_val = uf.n*10**np.ceil(-np.log10(np.abs(uf.n)))
		n_exp = int(np.floor(np.log10(np.abs(uf.n))))
		s_val = np.abs(uf.s)*10**np.ceil(-np.log10(np.abs(uf.s)))
		s_exp = int(np.floor(np.log10(uf.s)))
		n_representative_digits = n_exp-s_exp
		temp = '{:.' + str(n_representative_digits) + 'f}'
		temp = temp.format(n_val)
		temp = temp + '(' + str(int(s_val)) + ')'
		if np.floor(np.log10(np.fabs(uf.n))) != 0:
			temp = temp + '{:.100e}'.format(np.fabs(uf.n))[102:]
		if int(uf.s/np.fabs(uf.n)*1e6) != 0:
			return  temp# + ' ({:d} ppm)'.format(int(uf.s/np.fabs(uf.n)*1e6))
		return temp
