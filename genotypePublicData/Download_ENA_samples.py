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
class Download_ENA_samples:
    def __init__(self, samplesheet, download_location, aspera_binary='ascp', aspera_openssh='asperaweb_id_dsa.openssh'):
        '''Initiate download_ENA_samplesheet class by setting tax_id and library_strategy
        
        samplesheet(str)    Samplesheet downloaded from http://www.ebi.ac.uk/ena/data/warehouse/search
                            Reports tab, with all columns selected.
                            Can also be downloaded by running Download_ENA_samplesheet (see genotypePublicData README)
        download_location(str):   Location to store the downloaded fastq files at
        aspera_binary(str)  Location of the Aspera binary (default: use from PATH) 
        aspera_openssh(str)  Location of the Aspera openssh (default: use from PATH) 
        '''
        # os.path.expanduser changes ~ into homedir
        self.aspera_binary = os.path.expanduser(aspera_binary)
        self.aspera_openssh = os.path.expanduser(aspera_openssh)
        if not os.path.isdir(download_location):
            logging.error('Download destination directory '+download_location+' does not exist')
            raise RuntimeError('Download destination directory does not exist')
        self.download_location = download_location
        self.samplesheet = samplesheet
        self.include_list = []
        self.exclude_list = []
        
    def __check_if_aspera_exists(self, aspera_binary):
        '''Check if aspera location given in aspera_binary exists or is in PATH
        
           aspera_binary(str):   Location of the Aspera binary
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
    
    def set_aspera_binary(self, aspera_binary):
        '''Set path to aspera binary'''
        self.aspera_binary = aspera_binary
    
    def set_aspera_openssh(self, aspera_openssh):
        '''Set path to aspera openssh'''
        self.aspera_openssh = aspera_openssh   
        
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
            time.sleep(5)
        else: # total size is unknown
            logging.info("read %d\n" % (readsofar,))
            time.sleep(5)
      
    def __download_sample_with_aspera(self, fastq_aspera_link, download_location):
        '''Download fastq file using aspera
        
           fastq_aspera_link(str)   Aspera link to download
           download_location(str)   Location to save downloaded file at
        '''
        command = [self.aspera_binary,'-QT', '-l 2000m', '-i', self.aspera_openssh,fastq_aspera_link,download_location]
        logging.info('Downloading with the terminal command:\n'+' '.join(command))
        subprocess.call(command)
        
    def __check_md5(self, fastq_file, md5):
        '''Check if the md5sum of downloaded fastq file is correct

           fastq_file(str):   Location of fastq file to check md5 of
           md5(str):   md5sum to check if it is same as md5sum of fastq_file
        '''
        if not os.path.exists(fastq_file):
            logging.info(fastq_file+' does not exist')
            return False
        logging.info('Calculating md5 of '+fastq_file)
        with open(fastq_file,'rb') as file_to_check:
            data = file_to_check.read()    
            md5_returned = hashlib.md5(data).hexdigest()
        logging.info('Calculated md5 = '+md5_returned+', comparing to '+md5)
        if md5_returned == md5:
            logging.info('md5 sums are the same')
        else:
            logging.info('md5 sums are not the same')
        return md5_returned == md5

    def download_samples(self, download_protocol='aspera'):
        '''Download the samples using either aspera or ftp
        
           download_protocol(str):   Download protocol to use (def: aspera). Can only be aspera or ftp
        '''
        if download_protocol == 'aspera':
            self.__check_if_aspera_exists(self.aspera_binary)
            if not os.path.isfile(self.aspera_openssh):
                logging.error('openssh key for Aspera not found at '+self.aspera_openssh)
                raise RuntimeError('openssh key for Aspera not found at '+self.aspera_openssh)
            logging.info('Found aspera binary at '+self.aspera_binary)
        elif download_protocol != 'ftp':
            logging.error('download_protocol variable given to download_samples was '+download_protocol+', not aspera or ftp')
            raise RuntimeError('download protocol can only be aspera or ftp')
        included_samples = []
        print('Downloading samples to '+self.download_location)
        with open(self.samplesheet,'r', encoding='utf-8') as samplesheet_handle:
            samplesheet_header = samplesheet_handle.readline().split('\t')
            header_index = self.__get_all_indices(samplesheet_header)
            for line in samplesheet_handle:
                line = line.strip().split('\t')
                
                run_accessions = line[header_index['run_accession']].rstrip(';').split(';')
                for run_accession in run_accessions:
                    download_file_location = self.download_location+run_accession+'.fastq.gz'
                    # exclude list overrides include list
                    # first check if self.include_list is not empty, as include list should only be used when at least one sample is given
                    if self.include_list and run_accession in self.include_list:
                        included_samples.append(run_accession)
                        if run_accession not in self.exclude_list:
                            x = 0
                            while not self.__check_md5(download_file_location, line[header_index['fastq_md5']]):
                                if download_protocol == 'ftp':
                                    fastq_ftp_link = 'ftp://'+line[header_index['fastq_ftp']]
                                    logging.info('Downloading '+fastq_ftp_link+' using ftp to '+download_file_location+'...')
                                    urllib.request.urlretrieve(fastq_ftp_link, download_file_location, self.__reporthook)
                                elif download_protocol == 'aspera':
                                    fastq_aspera_link = 'era-fasp@'+line[header_index['fastq_aspera']]
                                    logging.info('Downloading '+fastq_aspera_link+' using aspera...')
                                    self.__download_sample_with_aspera(fastq_aspera_link, download_file_location)
                                else:
                                    logging.error('Download protocol was not ftp or aspera')
                                    raise RuntimeError('download protocol was not ftp or aspera')
                                x += 1
                                if x == 10:
                                    self.logging.warning('Tried 10 times to download '+run_accession+' but md5sum never correct. Skipping')
                                    break
        not_included_samples = [x for x in self.include_list if x not in included_samples]
        if len(not_included_samples):
            logging.warn('Not all samples from include list were present in the samplesheet. Missing: '+'\t'.join(not_included_samples))
    
