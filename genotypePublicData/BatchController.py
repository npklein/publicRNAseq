import logging
import sys
import os
from .Utils import Utils
from .Compute import Compute
from .Download_ENA_samples import Download_ENA_samples

format = '%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format=format)
class BatchController:
    def __init__(self, ena_samplesheet, samples_per_batch, project, root_dir, inclusion_list=None, exclusion_list=[],
                 compute_version='v16.11.1-Java-1.8.0_74'):
        '''Controller over downloading and dividing into batches of samples.
        
        ena_samplesheet(str)    Samplesheet downloaded from http://www.ebi.ac.uk/ena/data/warehouse/search
                            Reports tab, with all columns selected.
                            Can also be downloaded by running Download_ENA_samplesheet (see genotypePublicData README)
        samples_per_batch(int)    Number of samples to process in one batch
        project(str)    Project name
        root_dir(str)   Root dir of the project
        inclusion_list(list)    Samples to include from the samplesheet (def: [] -> no samples get excluded)
        exclusion_list(list)    Samples to exclude from teh samplesheet (def: None -> all samples get includes)
        '''
        self.script_dir = os.path.dirname(os.path.abspath(__file__))+'/'
        self.ena_samplesheet = ena_samplesheet
        self.inclusion_list = inclusion_list
        self.exclusion_list = exclusion_list
        self.samples_per_batch = samples_per_batch
        self.project = project
        self.root_dir = root_dir+'/'
        self.compute_version = compute_version
        if self.samples_per_batch < 1:
            logging.error('Need at least 1 sample per batch, now have '+str(self.samples_per_batch)+' samples in one batch')
        if not os.path.exists(self.ena_samplesheet):
            logging.error('Samplesheet '+samplesheet+' does not exist')
            raise RuntimeError('Samplesheet '+samplesheet+' does not exist')
        self.__create_batches()
        self.__create_folder_structure()

    def __create_batches(self):
        '''Create the batches by adding samples that are in the inclusion list (if None add all) and not in the exclusion list
           Exclusion list trumps inclusion list (sample in both inclusion and exclusion list will be excluded)'''
        self.batches = [{}]
        self.number_of_excluded_samples = 0
        included_samples = 0
        with open(self.ena_samplesheet,'r', encoding='utf-8') as input_file:
            samplesheet_header = input_file.readline().split('\t')
            samplesheet_header_index = Utils.get_all_indices(samplesheet_header)
            samples_in_current_batch = 0
            current_batch = 0
            for line in input_file:
                line = line.strip().split('\t')
                run_accession = line[samplesheet_header_index['run_accession']]
                if run_accession not in self.exclusion_list and (
                                        not self.inclusion_list or  run_accession in self.inclusion_list):
                        if samples_in_current_batch == self.samples_per_batch:
                            samples_in_current_batch = 0
                            current_batch += 1
                            self.batches.append({})
                        included_samples += 1
                        fastq_aspera_links = line[samplesheet_header_index['fastq_aspera']].rstrip(';').split(';')
                        fastq_aspera_links = [x.split('/')[-1] for x in fastq_aspera_links]
                        self.batches[current_batch][run_accession] = fastq_aspera_links
                        samples_in_current_batch += 1
                        assert samples_in_current_batch <= self.samples_per_batch
                else:
                    self.number_of_excluded_samples += 1
        logging.info('Excluded '+str(self.number_of_excluded_samples)+' samples.')
        logging.info('Included '+str(included_samples)+' samples.')
        logging.info(str(len(self.batches))+' batches made with in each batch '+str(len(self.batches[0]))+' samples and in the last batch '+
                     str(len(self.batches[-1]))+' samples.')
    
    def get_batches(self):
        return self.batches
    
    def __create_folder_structure(self):
        '''Create the batch folder structure for putting jobs/samplesheets/parameter files etc in'''
        logging.info('Creating dirctory '+self.root_dir+'/fastq_downloads/')
        os.makedirs(self.root_dir+'/fastq_downloads/', exist_ok=True)
        for batch in range(0, len(self.batches),1):
            logging.info('Creating directory '+self.root_dir+'/batch'+str(batch))
            os.makedirs(self.root_dir.rstrip('/')+'/batch'+str(batch), exist_ok=True)
    
    def __create_samples_per_batch_file(self):
        '''In the root folder, create a file that contains for each batch which samples are included'''
        outfile = self.root_dir+'/samples_per_batch.tsv'
        logging.info('Writing file containing the samples per batch to '+outfile)
        with open(outfile,'w') as out:
            for batch_number in range(0, len(self.batches),1):
                if batch_number >= 1:
                    out.write('\t')
                out.write('batch'+str(batch_number))
            out.write('\n')
            for batch_index, batch in enumerate(self.batches):
                out.write('\t'.join(self.batches[batch_index].keys())+'\n')
    
    def setup_project(self, echo_output=True):
        '''Setup the project by making the correct folder structure, writing samplesheet/parameter files, and Molgenis Compute scripts

        echo_output(bool):   Wether or not to echo compute output (mostly for testing purposes)
        '''
        # rstrip and later add the / so that the path is not printed with // when logging    
        compute = Compute(self.root_dir, self.batches, self.project)
        compute.get_molgenis_pipelines()
        self.__create_samples_per_batch_file()
        compute.create_parameter_files(self.script_dir+'/../configurations/')
        compute.create_QC_samplesheet()
        compute.create_molgenis_generate_jobs_script(self.compute_version)
        compute.generate_jobs(echo_output)
    
    def download_samples(self, batch_number, aspera_openssh='~/.aspera/connect/etc/asperaweb_id_dsa.openssh'):
        '''Download samples of certain batch
        
        batch_number(int):     Number of the batch to download samples for
        aspera_binary(str)  Location of the Aspera binary (default: use from PATH)
        aspera_openssh(str)  Location of the Aspera openssh (default: ~/.aspera/connect/etc/asperaweb_id_dsa.openssh)
        '''
        logging.info('Downloading '+str(len(self.batches[batch_number]))+' samples for batch '+str(batch_number)+' to '+self.root_dir+'/fastq_downloads/')
        download_samples = Download_ENA_samples(samplesheet = self.ena_samplesheet, 
                                                download_location = self.root_dir+'/fastq_downloads/',
                                                inclusion_list = self.batches[batch_number])
        download_samples.start()
