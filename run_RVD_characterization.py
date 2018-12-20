import threading
import os
from time import sleep

import directories as DIRS

N_SIMULTANEOUS_PROCESSING_THREADS = 4
N_MEASUREMENT_RUNS = 1

def measure(n_runs=1):
	if not isinstance(n_runs, int) or n_runs < 1:
		raise TypeError('"n_runs" must be a positive integer number')
	while n_runs > 0:
		print('Thread: ' + threading.current_thread().getName() + ' --> # of runs left = ' + str(n_runs))
		os.system("start /wait cmd /c python measure_many_frequencies.py")
		n_runs -= 1
	print('Measurements finished!')

def process_data():
	os.system("start /wait cmd /c python while_true_process_data.py")

def status(measuring_thread):
	while True:
		if measuring_thread.isAlive() is False:
			if len(os.listdir(DIRS.UNPROCESSED_DATA_PATH)) == 0: # This means that there is data awaiting to be processed.
				print('Thread: ' + threading.current_thread().getName() + ' --> Waiting 60 seconds to finish processing...')
				sleep(60)
				print('Thread: ' + threading.current_thread().getName() + ' --> Everything is done!')
				return
		sleep(1)

measuring_thread = threading.Thread(target=measure, name='measuring', args=(N_MEASUREMENT_RUNS,))
status_thread = threading.Thread(target=status, name='status', args=(measuring_thread,))
processing_threads = []
for k in range(N_SIMULTANEOUS_PROCESSING_THREADS):
	processing_threads.append(threading.Thread(target=process_data, name='process_data #'+str(k), daemon=True))

print('Running measurements...')
measuring_thread.start()
print('Running processing...')
for k in range(N_SIMULTANEOUS_PROCESSING_THREADS):
	processing_threads[k].start()
status_thread.start()
