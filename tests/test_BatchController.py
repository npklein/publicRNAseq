from context import genotypePublicData
import os
import unittest
import shutil

class BatchControlTest(unittest.TestCase):  
    def setUp(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))+'/'
        # Control Batches can be used to run the whole pipeline and divide the samples up in multiple batches for processing
        # Download starts per batch sequentially, then all jobs from that batch are submitted using Molgenis Compute, and then
        # the next batch starts downloading
        self.ena_samplesheet = self.script_dir+'test_data/ena_example_samplesheet.txt'
        self.output_root_dir = self.script_dir+'test_output/'
        self.project = 'test'
        shutil.rmtree(self.output_root_dir)
        os.mkdir(self.output_root_dir)
        # some samples need to be included from the samplesheet
        include_list = ['DRR000897','DRR001174']
        # some samples need to be excluded
        exclude_list = ['DRR001174']
        # folder structure is created when initializing
        self.batch_controller = genotypePublicData.BatchController(self.ena_samplesheet, samples_per_batch=2, project=self.project, 
                                                              root_dir=self.output_root_dir,inclusion_list=include_list, exclusion_list=exclude_list)
        # setup project by generating samplesheets, parameter files etc
        self.batch_controller.setup_project(echo_output=False)
<<<<<<< HEAD
        self.batch_controller.download_samples(0)
=======
>>>>>>> 147d2ac9ab5ac790a206a79537be432df03ffbc2
    def tearDown(self):
        pass

    def test_can_read_in_samplesheet_and_make_batches(self):  
<<<<<<< HEAD
        
        self.assertEqual(self.batch_controller.number_of_excluded_samples,7)
=======
        self.assertEqual(self.batch_controller.number_of_excluded_samples,9)
>>>>>>> 147d2ac9ab5ac790a206a79537be432df03ffbc2
        # We can get the created batches from batch_controller 
        batches = self.batch_controller.get_batches()
        # The batch controller should contain 2 batches, one with 2 samples and one with 1 sample
        print(batches)
        self.assertEqual(len(batches), 1, 'Does not contain 1 batches')
        self.assertEqual(batches, [{'DRR000897': ['DRR000897.fastq.gz']}])
 
        self.assertTrue(os.path.exists(self.output_root_dir+'molgenis-pipelines/'))
        for batch_number in range(0, len(batches),1):
            batch = 'batch'+str(batch_number)
            self.assertTrue(os.path.exists(self.output_root_dir+batch))
            self.assertTrue(os.path.exists(self.output_root_dir+batch+'/samplesheet_QC_batch'+str(batch_number)+'.csv'))
            self.assertTrue(os.path.exists(self.output_root_dir+batch+'/parameters_QC_batch'+str(batch_number)+'.csv'))
            self.assertTrue(os.path.exists(self.output_root_dir+batch+'/parameters_genotyping_'+batch+'.csv'))
            self.assertTrue(os.path.exists(self.output_root_dir+batch+'/generate_QCjobs_'+batch+'.sh'))
            lines = 0
            
            with open(self.output_root_dir+batch+'/parameters_QC_'+batch+'.csv') as input_file:
                for line in input_file:
                    lines += 1
                self.assertEqual(lines,2, 'Parameter file should be in long format, but has more than 2 lines')
            lines = 0
            with open(self.output_root_dir+batch+'/parameters_genotyping_'+batch+'.csv') as input_file:
                for line in input_file:
                    lines += 1
                self.assertEqual(lines,2, 'Parameter file should be in long format, but has more than 2 lines')        
            with open(self.output_root_dir+batch+'/generate_QCjobs_'+batch+'.sh') as input_file:
                generate_QC_jobs = input_file.read()
                self.assertTrue('module load Molgenis-Compute' in generate_QC_jobs, 'No module load in the QC generate script')
                self.assertTrue(batch in generate_QC_jobs, 'Wrong batch in generate QC jobs script')


        self.assertTrue(os.path.exists(self.output_root_dir+'fastq_downloads'))
        self.assertTrue(os.path.exists(self.output_root_dir+'samples_per_batch.tsv'))
        with open(self.output_root_dir+'samples_per_batch.tsv') as input_file:
            self.assertEqual(input_file.readline(),'batch0\n', 'Header samples_per_batch.tsv not correct')
            line1 = input_file.readline()
            samples_line1 = line1.strip().split('\t')
            self.assertTrue('DRR000897' in samples_line1, 'DRR000897 not on line 1')
            self.assertEqual(len(samples_line1), 1, 'Not 1 samples on line 1')
        
        
    def test_can_download_samples(self):
        '''Download the samples one batch at a time'''
        self.assertTrue(os.path.exists(self.output_root_dir+'/fastq_downloads/DRR000897.fastq.gz'))

    def test_can_submit_jobs(self):
        '''Download the samples one batch at a time'''
        self.batch_controller.submit_QC_batch(0)
        

    def test_can_submit_jobs(self):
        '''Download the samples one batch at a time'''
        self.batch_controller.submit_QC_batch(0)
        


if __name__ == '__main__':  
    unittest.main(warnings='ignore')  

