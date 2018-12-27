import threading
import os
from time import sleep

import directories as DIRS

N_SIMULTANEOUS_PROCESSING_THREADS = 4
N_MEASUREMENT_RUNS = 20

def process():
	print('Calling "process_data.py"')
	os.system("python process_data.py")

def measure(n_runs=1):
	if not isinstance(n_runs, int) or n_runs < 1:
		raise TypeError('"n_runs" must be a positive integer number')
	while n_runs > 0:
		print('Thread: ' + threading.current_thread().getName() + ' --> # of runs left = ' + str(n_runs))
		# ~ os.system("start /wait cmd /c python measure_many_frequencies.py")
		os.system("python measure_many_frequencies.py")
		n_runs -= 1
	print('Thread: ' + threading.current_thread().getName() + ' --> Measurements finished!')

def process_data(measuring_thread):
	processing_threads = []
	while measuring_thread.isAlive() is True or len(os.listdir(DIRS.UNPROCESSED_DATA_PATH)) > 0:
		if len(os.listdir(DIRS.UNPROCESSED_DATA_PATH)) > 0: # This means there is data awaiting to be processed.
			if len(processing_threads) < N_SIMULTANEOUS_PROCESSING_THREADS:
				print('Calling "fix_trigger_problem.py"')
				os.system("python fix_trigger_problem.py")
				processing_threads.append(threading.Thread(target=process))
				processing_threads[-1].start()
			else:
				for k in range(len(processing_threads)):
					if processing_threads[k].isAlive() is False: # This means that this thread is available to process new data.
						print('Calling "fix_trigger_problem.py"')
						os.system("python fix_trigger_problem.py")
						processing_threads[k] = threading.Thread(target=process)
						processing_threads[k].start()
					sleep(1) # This is to avoid two threads tying to process the same data.
		sleep(1)
	while True: # Check that all data has been processed.
		for k in range(len(processing_threads)):
			if processing_threads[k].isAlive() is False:
				processing_threads.pop(k)
		if len(processing_threads) == 0:
			print('Thread: ' + threading.current_thread().getName() + ' --> Processing finished')
			return
# ----------------------------------------------------------------------

measuring_thread = threading.Thread(target=measure, name='measuring', args=(N_MEASUREMENT_RUNS,))
data_processing_thread = threading.Thread(target=process_data, name='data processing', args=(measuring_thread,))

measuring_thread.start()
data_processing_thread.start()
print('Measuring and processing data...')
while data_processing_thread.isAlive() is True:
	sleep(1)
print('Processing transference data...')
os.system("python plot_transference.py")

# ~ sleep(1000)
# ~ os.system('shutdown -s')
