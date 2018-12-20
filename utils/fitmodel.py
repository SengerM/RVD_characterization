import uncertainties as unc
from uncertainties import unumpy as unp
import scipy.optimize as opt # This is used for fiting models and data.
import numpy as np
import nicenquickplotlib as nq
from . import my_uncertainties_utils as munc

def fit_bootstrap(p0, datax, datay, function, yerr_systematic=0.0):
	# This function was taken from here: https://stackoverflow.com/questions/14581358/getting-standard-errors-on-fitted-parameters-using-the-optimize-leastsq-method-i
    errfunc = lambda p, x, y: function(x,p) - y
    # Fit first time
    pfit, perr = opt.leastsq(errfunc, p0, args=(datax, datay), full_output=0)
    # Get the stdev of the residuals
    residuals = errfunc(pfit, datax, datay)
    sigma_res = np.std(residuals)
    sigma_err_total = np.sqrt(sigma_res**2 + yerr_systematic**2)
    # 100 random data sets are generated and fitted
    ps = []
    for i in range(100):
        randomDelta = np.random.normal(0., sigma_err_total, len(datay))
        randomdataY = datay + randomDelta
        randomfit, randomcov = opt.leastsq(errfunc, p0, args=(datax, randomdataY), full_output=0)
        ps.append(randomfit) 
    ps = np.array(ps)
    mean_pfit = np.mean(ps,0)
    # You can choose the confidence interval that you want for your
    # parameter estimates: 
    Nsigma = 1. # 1sigma gets approximately the same as methods above
                # 1sigma corresponds to 68.3% confidence interval
                # 2sigma corresponds to 95.44% confidence interval
    err_pfit = Nsigma * np.std(ps,0) 

    pfit_bootstrap = mean_pfit
    perr_bootstrap = err_pfit
    return pfit_bootstrap, perr_bootstrap


class fitmodel:
	"""
	La idea de la clase 'fitmodel' es crear un modelo matemático para ajustar a datos. Es una
	clase sencilla pero que facilita la vida a la hora de hacer ajustes de varios modelos a 
	varios datos a la vez, haciendo que cada modelo y cada ajuste esté encapsulado en un objeto
	distinto (de la clase fitmodel).
	La clase tiene los siguientes atributos:
		self.func: Es la función matemática que se desea ajustar a los datos. Tiene que ser de la
					forma 'f(x, p[]) siendo x la variable independiente y p[] la lista de parámetros
					que se ajustarán.
		self._params: Es la lista de parámetros ajustados. Cuando se crea una instancia de la clase
					'fitmodel' se inicializan todos los parámetros a 'None' indicando que aún no
					se ha realizado ninguna estimación de los mismos.
		self.str_formula: Es una cadena que dice cuál es la fórmula matemática del modelo. Esta 
					cadena es la que se imprimirá siempre que haya que imprimir la fórmula analítica.
					Se puede escribir en Latex, por ejemplo: r'Cadena en Latex $frac{x}{y}$'.
		self.str_params: Es una lista de cadenas que dice cómo se llama cada uno de los parámetros
					en 'self._params'. Cuando haya que imprimir el nombre de un parámetro, se usará
					el dato almacenado en 'str_params'.
		self._xdata/_ydata: Acá se cargan los datos que se usarán para el ajuste. Cada vez que se
					cargan datos nuevos, se borran los parámetros ajustados previamente (si los hubiere).
		self.name: Una cadena con un nombre de pila (opcional) para el modelo.
	
	Los pasos para usar un objeto de esta clase en forma exitosa son los siguientes:
		1) Crear el objeto.
		2) Cargarle los datos (x,y) para realizar el ajuste usando el método "set_data".
		3) Ajustar los datos llamando al método "fit".
		4) Graficar el ajuste llamando al método "plot_model_vs_data".
	
	"""
	def __init__(self, func, str_formula, str_params, name=None):
		self.func = func # func must be of the form "func(x, p)" with p[0], p[1], ... the params.
		self.str_formula = str_formula # Formula to be printed for this model.
		self.str_params = str_params # Params as they should be printed.
		self._params = [None]*len(str_params) # Here will be stored the values of the fitted params.
		self._xdata = [None]
		self._ydata = [None]
		self.name = name
	
	def set_data(self, xdata, ydata):
		"""
		xdata and ydata must be numpy arrays or ufloat arrays.
		"""
		if len(xdata) != len(ydata):
			raise ValueError('Length of xdata and ydata does not match')
		self._params = [None]*len(self.str_params)
		if not isinstance(xdata[0], unc.UFloat):
			xdata = unp.uarray(xdata, xdata*0)
		if not isinstance(ydata[0], unc.UFloat):
			ydata = unp.uarray(ydata, ydata*0)
		self._xdata = xdata
		self._ydata = ydata
		
	def fit(self, p0=[None]):
		"""
		Ajusta el modelo a los datos provistos. Los parámetros estimados con el ajuste
		se almacenan en 'self._params'.
		"""
		if self._xdata[0] == None or self._ydata[0] == None:
			raise ValueError('No data provided for fitting!')
		if p0[0] == None:
			p0 = [0.0]*len(self._params)
		else:
			if len(p0) != len(self._params):
				raise ValueError('len(p0) != number of params required by this model')
		if isinstance(p0[0], unc.UFloat):
			p0 = unp.nominal_values(p0)
		if isinstance(self._xdata[0], unc.UFloat):
			xdata = unp.nominal_values(self._xdata)
		else:
			xdata = self._xdata
		if isinstance(self._ydata[0], unc.UFloat):
			ydata = unp.nominal_values(self._ydata)
			yerr = unp.std_devs(self._ydata)
		else:
			ydata = self._ydata
			yerr = np.zeros(len(ydata))
		
		def float_func(x, p):
			return unp.nominal_values(self.func(x, p))
		pfit, perr = fit_bootstrap(p0, xdata, ydata, float_func, yerr)
		for k in range(len(p0)):
			self._params[k] = unc.ufloat(pfit[k], perr[k])
	
	def __str__(self):
		string = 'Fitmodel object\n'
		if not self.name == None:
			string += 'Model name: ' + self.name + '\n'
		string += self.str_formula + '\n'
		if self._params[0] == None:
			string += 'No data fitted yet'
		else:
			string += 'Current estimated params:\n'
			for k in range(len(self._params)):
				string += '\t' + self.str_params[k] + ' = ' + munc.ufloat_nice_str(self._params[k]) + '\n'
		return string
	
	def param_val(self, key):
		return self._params[key]
	
	def print_nice_box(self, axes, x_pos=0.1, y_pos=0.95, BBOX=dict(boxstyle='round', facecolor='white', edgecolor=(.7,.7,.7), alpha=0.8)):
		"""
		Imprime información concerniente al modelo (fórmula, parámetros y valores estimados) de una
		forma fachera en un recuadro adentro de una figura.
		"""
		# ~ data_str = 'Model: '
		# ~ if not self.name == None:
			# ~ data_str += self.name + ', '
		data_str = self.str_formula + '\n'
		for k in range(len(self._params)):
			data_str += self.str_params[k] + r'$=$' + munc.ufloat_nice_str(self._params[k]) + '\n'
		axes.text(x_pos, y_pos, data_str, transform=axes.transAxes, verticalalignment='top', bbox=BBOX)
	
	def plot_model_vs_data(self, nicebox=False, *args, **kwargs):
		"""
		Plotea en un gráfico los datos (x,y) cargados en el modelo, superpuestos con el
		modelo (previamente ajustado) evaluado en los valores de xdata cargados.
		"""
		if self._params[0] == None:
			raise ValueError('Impossible to eval model: params has not yet ben estimated! (no data fitted)')
		else:
			if isinstance(self._xdata[0], unc.UFloat):
				xdata = unp.nominal_values(self._xdata)
			else:
				xdata = self._xdata
		fig = nq.plot(xdata, [self._ydata, self.eval(xdata)], legend=['Data', 'Fit'], linestyle=['-','--'], title=self.name, *args, **kwargs)
		if nicebox is True:
			self.print_nice_box(fig.axes[0])
		return fig
	
	def plot_residuals(self, *args, **kwargs):
		"""
		Plotea los residuos del ajuste.
		"""
		if self._params[0] == None:
			raise ValueError('Impossible to eval model: params has not yet ben estimated! (no data fitted)')
		else:
			if isinstance(self._xdata[0], unc.UFloat):
				xdata = unp.nominal_values(self._xdata)
			else:
				xdata = self._xdata
			nq.plot(xdata, self._ydata - self.eval(xdata), *args, **kwargs)
	
	def eval(self, x_data):
		"""
		Evalúa el modelo sobre un array de datos.
		"""
		if self._params[0] == None:
			raise ValueError('Impossible to eval model: params has not yet ben estimated! (no data fitted)')
		else:
			return self.func(x_data, self._params)
