import logging
import sys
format = '%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format=format)
import time
import requests

class Download_ENA_samples:
    def __enter__(self):
        '''Using __enter__ to be able to use with Download_ENA_samples, so that the samplesheet file handle is opened and closed properly
        '''
        self.samplesheet_handle = open(samplesheet,'r')
        
    def __init__(self, samplesheet):
        '''Initiate download_ENA_samplesheet class by setting tax_id and library_strategy

        samplesheet(str)    Samplesheet downloaded from http://www.ebi.ac.uk/ena/data/warehouse/search?query=%22tax_eq%289606%29%20AND%20library_strategy=%22RNA-Seq%22%22&domain=read
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
        
    def download_samples(self):
        samplesheet_header = self.samplesheet_handle.readline()
        header_index = self.__get_all_indices(samplesheet_header)
        for line in self.samplesheet_handle:
            line = line.strip().split('\t')
            run_accession = line[header_index['run_accession']]
            # first check if self.include_list is not empty, as include list should only be used when at least one sample is given
            # exclude list overrides include list
            if self.include_list and run_accession in self.include_list and run_accession not in self.exclude_list:
                print(line)
    
    def __exit__(self):
        self.samplesheet_handle.close()     