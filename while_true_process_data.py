import os
from time import sleep
import numpy as np

while True:
	os.system("python process_data.py")
	sleep(np.random.uniform(1,5))
