import logging
import sys
import time
import requests
import os
import urllib.request 
import subprocess
import hashlib

format = '%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format=format)
class Run_compute:
    def __init__(self, compute_location, samplesheet, jobs_folder):
        '''Initiate Run_compute class
        
        samplesheet(str)    Samplesheet downloaded from http://www.ebi.ac.uk/ena/data/warehouse/search
                            Reports tab, with all columns selected.
                            Can also be downloaded by running Download_ENA_samplesheet (see genotypePublicData README)
        '''
        self.samplesheet = samplesheet
        self.include_list = []
        self.exclude_list = []
        
    def set_include_list(self, include_list):
        '''Samples to include for download'''
        self.include_list = include_list
    
    def set_exclude_list(self, exclude_list):
        '''Samples to exclude for download'''
        self.exclude_list = exclude_list
       
    def __check_if_compute_exists(self, compute_sh):
        '''Check if compute location given in compute_sh exists or is in PATH
        
           compute_sh(str):   Location of the compute sh script
           aspera_openssh(str)  Location of the Aspera openssh
        '''
        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        fpath, fname = os.path.split(aspera_binary)
        if fpath:
            if is_exe(aspera_binary):
                return aspera_binary
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, aspera_binary)
                if is_exe(exe_file):
                    return exe_file
        logging.error(aspera_binary+' does not exist and is not found in PATH. Set correct location for binary and openssh key '+
                      'when initiating Download_ENA_samples class or with set function')        
        raise RuntimeError('Aspera binary not found')
        
    def make_jobs(self):
        