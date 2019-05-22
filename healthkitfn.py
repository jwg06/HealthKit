#Imports for Functions
import logging
import zipfile
import os
import shutil

#Logging Function
def init_logging():
    rootLogger = logging.getLogger('healthkit_logger')

    LOG_DIR = os.getcwd() + '/' + 'logs'
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    fileHandler = logging.FileHandler("{0}/{1}.log".format(LOG_DIR, "healthkit"))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fileHandler.setFormatter(formatter)

    rootLogger.addHandler(fileHandler)

    rootLogger.setLevel(logging.DEBUG)

    consoleHandler = logging.StreamHandler()
    rootLogger.addHandler(consoleHandler)

    return rootLogger



