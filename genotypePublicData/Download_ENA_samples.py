import logging
import sys
import time
import requests
import os
import urllib.request 
format = '%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format=format)
class Download_ENA_samples:
    def __init__(self, samplesheet, aspera_binary='ascp'):
        '''Initiate download_ENA_samplesheet class by setting tax_id and library_strategy
        
        aspera_binary(str)  Location of the Aspera binary (default: use from PATH) 
        samplesheet(str)    Samplesheet downloaded from http://www.ebi.ac.uk/ena/data/warehouse/search?query=%22tax_eq%289606%29%20AND%20library_strategy=%22RNA-Seq%22%22&domain=read
                            Reports tab, with all columns selected.
                            Can also be downloaded by running Download_ENA_samplesheet (see genotypePublicData README)
        '''
        self.aspera = self.__check_if_aspera_exists(aspera_binary)
        self.samplesheet = samplesheet
        self.include_list = []
        self.exclude_list = []
        
    def __check_if_aspera_exists(self, aspera_binary):
        '''Check if aspera location given in aspera_binary exists or is in PATH
        
           aspera_binary(str):   Location of the Aspera binary
        '''
        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        fpath, fname = os.path.split(aspera_binary)
        if fpath:
            if is_exe(program):
                return program
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, aspera_binary)
                if is_exe(exe_file):
                    return exe_file
        logging.error(aspera_binary+' does not exist and is not found in PATH. Set correct location for binary when initiating Download_ENA_samples class')        
        raise RuntimeError('Aspera binary not found')
    
    def set_include_list(self, include_list):
        '''Samples to include for download'''
        self.include_list = include_list
    
    def set_exclude_list(self, exclude_list):
        '''Samples to exclude for download'''
        self.exclude_list = exclude_list
    
    def __get_all_indices(self, list_to_index):
        '''Get the indexes of all the items in a list and put them in a dict with key: element, value: index
        
           list_to_index(list)    List to get index from all elements from
        '''
        list_indexes = {}
        i = 0
        for element in list_to_index:
            list_indexes[element] = i
            i += 1
        return list_indexes
    
    def __reporthook(self,blocknum, blocksize, totalsize):
        ''' Report hook for urlretrieve
        Copied from: http://stackoverflow.com/a/13895723/651779
        '''
        readsofar = blocknum * blocksize
        if totalsize > 0:
            percent = readsofar * 1e2 / totalsize
            s = "\r%5.1f%% %*d / %d" % (
                percent, len(str(totalsize)), readsofar, totalsize)
            logging.info(s)
            if readsofar >= totalsize: # near the end
                logging.info("\n")
        else: # total size is unknown
            logging.info("read %d\n" % (readsofar,))
    
        
    def download_samples(self):
        included_samples = []
        with open(self.samplesheet,'r', encoding='utf-8') as samplesheet_handle:
            samplesheet_header = samplesheet_handle.readline().split('\t')
            header_index = self.__get_all_indices(samplesheet_header)
            for line in samplesheet_handle:
                line = line.strip().split('\t')
                
                run_accessions = line[header_index['run_accession']].rstrip(';').split(';')
                for run_accession in run_accessions:
                    # first check if self.include_list is not empty, as include list should only be used when at least one sample is given
                    # exclude list overrides include list
                    if self.include_list and run_accession in self.include_list:
                        included_samples.append(run_accession)
                        if run_accession not in self.exclude_list:
                            fastq_file = 'ftp://'+line[header_index['fastq_ftp']]
                            logging.info('Downloading '+fastq_file+'...')
                            urllib.request.urlretrieve(fastq_file, '/tmp/'+fastq_file.split('/')[-1], self.__reporthook)
        not_included_samples = [x for x in self.include_list if x not in included_samples]
        if len(not_included_samples):
            logging.warn('Not all samples from include list were present in the samplesheet. Missing: '+'\t'.join(not_included_samples))
    