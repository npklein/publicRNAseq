import subprocess
import logging
import sys
import os
from .Utils import Utils
import git

format = '%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format=format)
class Compute:
    '''Class for working around compute: creating samplesheets, parameter files, generating scripts etc'''
    def __init__(self, root_dir, batches, project):
        '''
        root_dir(str)   Root dir of the project
        project (str)   project name
        batches (dir)   Samples per batch 
        '''
        self.root_dir = root_dir
        self.batches = batches
        self.project = project
        
    def create_QC_samplesheet(self):
        '''For each batch, create a samplesheet that compute can use'''
        for batch_number in range(0,len(self.batches),1):
            batch = 'batch'+str(batch_number)
            molgenis_samplesheet = self.root_dir+'/'+batch+'/samplesheet_QC_batch'+str(batch_number)+'.csv'
            logging.info('Creating samplesheet at '+molgenis_samplesheet)
            with open(molgenis_samplesheet,'w') as out:
                out.write('internalId,project,sampleName,reads1FqGz,reads2FqGz\n')
                for sample in self.batches[batch_number]:
                    number_of_fastq_files = len(self.batches[batch_number][sample])
                    if number_of_fastq_files == 1:
                        out.write(sample+','+self.project+','+sample+','+
                                  self.root_dir+'/fastq_downloads/'+self.batches[batch_number][sample][0]+',\n')
                    elif number_of_fastq_files == 2 or number_of_fastq_files == 3:
                        out.write(sample+','+self.project+','+sample+','+
                                  self.root_dir+'/fastq_downloads/'+self.batches[batch_number][sample][0]+','+
                                  self.root_dir+'/fastq_downloads/'+self.batches[batch_number][sample][1]+'\n')
                    else:
                        logging.error('Number of files for '+sample+' is '+str(number_of_fastq_files)+' dont know what to do if it')
                        RuntimeError('Wrong number of fastq files for '+samples)
    
    def create_molgenis_generate_jobs_script(self, compute_version):
        '''For each batch, create a molgenis generate script
    
        compute_version (str)   Version of compute to use
        '''
        for batch_number in range(0, len(self.batches),1):
            batch = 'batch'+str(batch_number)
            generate_QCjobs_file = self.root_dir+'/'+batch+'/generate_QCjobs_'+batch+'.sh'
            with open(generate_QCjobs_file,'w') as out:
                out.write('set -e\n')
                out.write('module load Molgenis-Compute/'+compute_version+'\n')
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

    def create_parameter_files(self, parameter_configuration_dir):
        '''For each batch, create parameter files
        
        parameter_configuration (str)   Directory with files with parameter configurations
        '''
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
        parameter_QC_file = parameter_configuration_dir+'/parameters_QC_template.csv'
        parameter_genotype_file = parameter_configuration_dir+'/parameters_genotyping_template.csv'
        if not os.path.exists(parameter_QC_file):
            logging.error('Parameter QC file does not exist at '+parameter_QC_file)
            raise RuntimeError('Parameter QC file does not exist at '+parameter_QC_file)
        if not os.path.exists(parameter_genotype_file):
            logging.error('Parameter genotype file does not exist at '+parameter_genotype_file)
            raise RuntimeError('Parameter genotype file does not exist at '+parameter_genotype_file)

        template_QC = convert_to_long_format(parameter_QC_file) 
        template_genotyping = convert_to_long_format(parameter_genotype_file)                    
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
    
    def get_molgenis_pipelines(self):
        '''Download the molgenis pipelines from github'''
        logging.info('Cloning molgenis-pipelines')
        try:        
            git.Repo.clone_from('https://github.com/molgenis/molgenis-pipelines.git', self.root_dir+'/molgenis-pipelines/')
        except git.exc.GitCommandNotFound:
            logging.error('Possible that git could not be located. Put in path or module load it before running code')
            raise
                        
    def generate_jobs(self, echo_output=True):
        '''Use Compute to generate jobs'''
        logging.info('Compute generating jobs')
        for batch_number in range(0, len(self.batches),1):
            batch = 'batch'+str(batch_number)
            generate_QCjobs_file = self.root_dir+'/'+batch+'/generate_QCjobs_'+batch+'.sh'
            logging.info('Execute "bash '+generate_QCjobs_file+'"')
            if not echo_output:
                with open(os.devnull, 'wb') as devnull:
                    subprocess.check_call(['bash', generate_QCjobs_file], stdout=devnull, stderr=subprocess.STDOUT)
            else:
                subprocess.check_call(['bash', generate_QCjobs_file])        
