import os

# Main directory for the current measurement:
CURRENT_MEASUREMENT_DIR = 'current_measurement'
CURRENT_MEASUREMENT_PATH = CURRENT_MEASUREMENT_DIR + '/'

UNPROCESSED_DATA_DIR = 'crude_data'
UNPROCESSED_DATA_PATH = CURRENT_MEASUREMENT_PATH + UNPROCESSED_DATA_DIR + '/'

TRIGGER_PROBLEM_FIXED_DATA_DIR = 'trigger_fixed_data'
TRIGGER_PROBLEM_FIXED_DATA_PATH = CURRENT_MEASUREMENT_PATH + TRIGGER_PROBLEM_FIXED_DATA_DIR + '/'

CURRENTLY_PROCESSING_DATA_DIR = 'currently_processing'
CURRENTLY_PROCESSING_DATA_PATH = CURRENT_MEASUREMENT_PATH + CURRENTLY_PROCESSING_DATA_DIR + '/'

PROCESSED_DATA_DIR = 'processed_data' 
PROCESSED_DATA_PATH = CURRENT_MEASUREMENT_PATH + PROCESSED_DATA_DIR + '/'

TRANSFERENCE_RESULTS_DIR = 'transference_results'
TRANSFERENCE_RESULTS_PATH = CURRENT_MEASUREMENT_PATH + TRANSFERENCE_RESULTS_DIR + '/'

CONFIG_FILE_SUFFIX = '_config.txt'
SAMPLES_FILE_SUFFIX = '_samples.txt'
TRANSFERENCE_FILE_SUFFIX = '_transference.txt'

correction_transference_file = 'Resultados/1806261156 - Voltimetros midiendo solo al generador (usar esta para calcular correccion sistematica)/Transference results/' + TRANSFERENCE_FILE_SUFFIX


def remove_dir(d):
    for path in (os.path.join(d,f) for f in os.listdir(d)):
        if os.path.isdir(path):
            remove_dir(path)
        else:
            os.unlink(path)
    os.rmdir(d)

def create_directories_structure():
	if CURRENT_MEASUREMENT_DIR not in os.listdir():
		os.makedirs(UNPROCESSED_DATA_PATH)
		os.makedirs(CURRENTLY_PROCESSING_DATA_PATH)
		os.makedirs(PROCESSED_DATA_PATH)
		os.makedirs(TRIGGER_PROBLEM_FIXED_DATA_PATH)

create_directories_structure()
