import requests
import logging

class Download_ENA_samplesheet:
    def __init__(self,tax_id='9606', library_strategy='RNA-seq'):
        '''Initiate download_ENA_samplesheet class by setting tax_id and library_strategy

        tax_id(str)    Organism to download samplesheet for (def: 9606 <homo sapiens>)
        library_strategy(str)    type of data to download (def: RNA-seq)
        '''
        self.tax_id = tax_id
        self.library_strategy = library_strategy

    def download_samplesheet(self, output_file, tax_id='9606',library_strategy='RNA-seq'):
        '''Download samplesheet from ENA
        output_file(str)    output file name for samplesheet    
        '''
        logging.info('Downloading samplesheet for tax_id: '+self.tax_id+' and library strategy: '+self.library_strategy)
        url = 'http://www.ebi.ac.uk/ena/data/warehouse/search?query=%22tax_eq('+tax_id+')%20AND%20library_strategy=%22'+library_strategy+'%22%22&domain=read'

        response = requests.get(url)

    def set_tax_id(self,taxid):
        self.tax_id = tax_id

    def set_library_strategy(self,library_strategy):
        self.library_strategy = library_strategy
