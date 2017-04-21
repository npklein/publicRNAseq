import logging
import sys
import os
from .Utils import Utils

format = '%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format=format)
class Samplesheets:
    '''Class for creating and maintaining compute samplesheets'''
    def create_QC_samplesheet(self, project, root_dir, batches):
        '''For each batch, create a samplesheet that compute can use
        
        project (str)    Project name to fill in samplesheet
        root_dir (str)   Directory where to place the samplesheet in
        batches (dir)    Samples per batch to add to samplesheet
        '''
        for batch_number in range(0,len(batches),1):
            batch = 'batch'+str(batch_number)
            molgenis_samplesheet = root_dir+'/'+batch+'/samplesheet_QC_batch'+str(batch_number)+'.csv'
            logging.info('Creating samplesheet at '+molgenis_samplesheet)
            with open(molgenis_samplesheet,'w') as out:
                out.write('internalId,project,sampleName,reads1FqGz,reads2FqGz\n')
                for sample in batches[batch_number]:
                    number_of_fastq_files = len(batches[batch_number][sample])
                    if number_of_fastq_files == 1:
                        out.write(sample+','+self.project+','+sample+','+
                                  root_dir+'/fastq_downloads/'+batches[batch_number][sample][0]+',\n')
                    elif number_of_fastq_files == 2 or number_of_fastq_files == 3:
                        out.write(sample+','+self.project+','+sample+','+
                                  root_dir+'/fastq_downloads/'+batches[batch_number][sample][0]+','+
                                  root_dir+'/fastq_downloads/'+batches[batch_number][sample][1]+'\n')
                    else:
                        logging.error('Number of files for '+sample+' is '+str(number_of_fastq_files)+' dont know what to do if it')
                        RuntimeError('Wrong number of fastq files for '+samples)
