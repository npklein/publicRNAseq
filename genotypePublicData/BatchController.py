import logging
import sys
import os
from .Utils import Utils
from .Samplesheets import Samplesheets
import git

format = '%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format=format)
class BatchController:
    def __init__(self, samplesheet, samples_per_batch, project, root_dir, inclusion_list=None, exclusion_list=[],
                 compute_version='v16.11.1-Java-1.8.0_74'):
        '''Controller over downloading and dividing into batches of samples.
        
        samplesheet(str)    Samplesheet downloaded from http://www.ebi.ac.uk/ena/data/warehouse/search
                            Reports tab, with all columns selected.
                            Can also be downloaded by running Download_ENA_samplesheet (see genotypePublicData README)
        samples_per_batch(int)    Number of samples to process in one batch
        project(str)    Project name
        root_dir(str)   Root dir of the project
        inclusion_list(list)    Samples to include from the samplesheet (def: [] -> no samples get excluded)
        exclusion_list(list)    Samples to exclude from teh samplesheet (def: None -> all samples get includes)
        '''
        self.script_dir = os.path.dirname(os.path.abspath(__file__))+'/'
        self.samplesheet = samplesheet
        self.inclusion_list = inclusion_list
        self.exclusion_list = exclusion_list
        self.samples_per_batch = samples_per_batch
        self.project = project
        self.root_dir = root_dir+'/'
        self.compute_version = compute_version
        if self.samples_per_batch < 1:
            logging.error('Need at least 1 sample per batch, now have '+str(self.samples_per_batch)+' samples in one batch')
        if not os.path.exists(self.samplesheet):
            logging.error('Samplesheet '+samplesheet+' does not exist')
            raise RuntimeError('Samplesheet '+samplesheet+' does not exist')
        self.__create_batches()
        
    def __create_batches(self):
        '''Create the batches by adding samples that are in the inclusion list (if None add all) and not in the exclusion list
           Exclusion list trumps inclusion list (sample in both inclusion and exclusion list will be excluded)'''
        self.batches = [{}]
        self.number_of_excluded_samples = 0
        included_samples = 0
        with open(self.samplesheet,'r', encoding='utf-8') as input_file:
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
    
    def __create_parameter_files(self):
        '''For each batch, create parameter files'''
        def convert_to_long_format(parameter_file):
            transposed_parameter_text = ''
            with open(parameter_file) as input_file:
                header = []
                values = []
                for line in input_file:
                    if line.startswith('#') or len(line.strip()) == 0:
                        continue
                    line = line.strip().split(',')
                    header.append(line[0])
                    values.append(line[1])
                for index in range(0,len(header),1):
                    transposed_parameter_text += header[index]+','
                transposed_parameter_text += '\n'
                for index in range(0,len(header),1):
                    transposed_parameter_text += values[index]+','
            return transposed_parameter_text
        template_QC = convert_to_long_format(self.script_dir+'../configurations/parameters_QC_template.csv') 
        template_genotyping = convert_to_long_format(self.script_dir+'../configurations/parameters_genotyping_template.csv')                    
        for batch_number in range(0,len(self.batches),1):
            batch = 'batch'+str(batch_number)
            parameters_QC_file = self.root_dir+'/'+batch+'/parameters_QC_batch'+str(batch_number)+'.csv'
            outfile_genotyping = self.root_dir+'/'+batch+'/parameters_genotyping_batch'+str(batch_number)+'.csv'
            logging.info('Creating QC pipeline parameter file at '+parameters_QC_file)
            logging.info('Creating genotyping pipeline parameter file at '+outfile_genotyping)
            new_template_QC = template_QC.replace('PROJECT_DIR_DO_NOT_CHANGE_THIS', self.root_dir+'batch'+str(batch_number)+'/results/')
            new_template_genotyping = template_QC.replace('PROJECT_DIR_DO_NOT_CHANGE_THIS', self.root_dir+'batch'+str(batch_number)+'/results/')
            with open(parameters_QC_file,'w') as out:
                out.write(new_template_QC)
            with open(outfile_genotyping,'w') as out:
                out.write(new_template_genotyping)
                    
    def __create_molgenis_generate_jobs_script(self):
        '''For each batch, create a molgenis generate script'''
        for batch_number in range(0, len(self.batches),1):
            batch = 'batch'+str(batch_number)
            generate_QCjobs_file = self.root_dir+'/'+batch+'/generate_QCjobs_'+batch+'.sh'
            with open(generate_QCjobs_file,'w') as out:
                out.write('set -e\n')
                out.write('module load Molgenis-Compute/'+self.compute_version+'\n')
                out.write('sh $EBROOTMOLGENISMINCOMPUTE/molgenis_compute.sh \\\n')
                out.write('  --backend slurm \\\n')
                out.write('  --generate \\\n')
                parameters_QC_file = self.root_dir+'/'+batch+'/parameters_QC_batch'+str(batch_number)+'.csv'
                out.write('  -p '+parameters_QC_file+' \\\n')
                molgenis_samplesheet = self.root_dir+'/'+batch+'/samplesheet_QC_batch'+str(batch_number)+'.csv'
                out.write('  -p '+molgenis_samplesheet+' \\\n')
                workflow_location = self.root_dir+'molgenis-pipelines/compute5/Public_RNA-seq_QC/workflows/workflow.csv'
                out.write('  -w '+workflow_location+' \\\n')
                out.write('  -rundir '+self.root_dir+'/'+batch+'/rundirs/QC/ --weave')

    
    def __get_molgenis_pipelines(self):
        '''Download the molgenis pipelines from github'''
        logging.info('Cloning molgenis-pipelines')
        try:        
            git.Repo.clone_from('https://github.com/molgenis/molgenis-pipelines.git', self.root_dir+'/molgenis-pipelines/')
        except git.exc.GitCommandNotFound:
            logging.error('Possible that git could not be located. Put in path or module load it before running code')
            raise
    
    def __generate_jobs(self):
        '''Use Compute to generate jobs'''
        logging.info('Compute generating jobs')
        for batch_number in range(0, len(self.batches),1):
            batch = 'batch'+str(batch_number)
            generate_QCjobs_file = self.root_dir+'/'+batch+'/generate_QCjobs_'+batch+'.sh'
            logging.info('Execute "bash '+generate_QCjobs_file+'"')
            os.system('bash '+generate_QCjobs_file)
        
    def setup_project(self):
        '''Setup the project by making the correct folder structure, writing samplesheet/parameter files, and Molgenis Compute scripts'''
        # rstrip and later add the / so that the path is not printed with // when logging    
        self.__create_folder_structure()
        self.__get_molgenis_pipelines()
        self.__create_samples_per_batch_file()
        self.__create_parameter_files()
        print(self.batches)
        Samplesheets.create_QC_samplesheet()
        self.__create_molgenis_generate_jobs_script()
        self.__generate_jobs()
