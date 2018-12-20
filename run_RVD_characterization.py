import threading
import os

N_PROCESSING_THREADS = 4

def measure(n_runs=1):
	if not isinstance(n_runs, int) or n_runs < 1:
		raise TypeError('"n_runs" must be a positive integer number')
	while n_runs > 0
		print('Thread: ' + threading.current_thread().getName() + ' --> # of runs left = ' + str(n_runs))
		os.system("start /wait cmd /c python measure_many_frequencies.py")
		n_runs -= 1
	print('Measurements finished!')

def process_data():
	os.system("start /wait cmd /c python while_true_process_data.py")

measuring_thread = threading.Thread(target=measure, name='measuring_thread', args=2)
processing_threads = []
for k in range(N_PROCESSING_THREADS):
	processing_threads.append(threading.Thread(target=process_data, name='process_data_thread#'+str(k)))

print('Running measurements...')
measuring_thread.start()
print('Running processing...')
for k in range(len(processing_threads)):
	processing_threads[k].start()
