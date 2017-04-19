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

    def tearDown(self):
        pass

    def test_can_read_in_samplesheet_and_make_batches(self):  
        # some samples need to be included from the samplesheet
        include_list = ['DRR000897','DRR001173','DRR001174','DRR001622']
        # some samples need to be excluded
        exclude_list = ['DRR001174']
        batch_controller = genotypePublicData.BatchController(self.ena_samplesheet, samples_per_batch=2, project=self.project, 
                                                              root_dir=self.output_root_dir,inclusion_list=include_list, exclusion_list=exclude_list)
        self.assertEqual(batch_controller.number_of_excluded_samples,7)
        # We can get the created batches from batch_controller 
        batches = batch_controller.get_batches()
        # The batch controller should contain 2 batches, one with 2 samples and one with 1 sample
        self.assertEqual(len(batches), 2, 'Does not contain 2 batches')
        self.assertEqual(batches, [{'DRR000897':['DRR000897.fastq.gz'],
                                   'DRR001173':['DRR001173.fastq.gz']},
                                   {'DRR001622':['DRR001622_1.fastq.gz','DRR001622_2.fastq.gz']}], 'Batch list not the same')
                
        # We want to set up the project first by creating the directory structure necesarry for putting jobs and results in
        batch_controller.setup_project()
        for batch_number in range(0, len(batches),1):
            batch = 'batch'+str(batch_number)
            self.assertTrue(os.path.exists(self.output_root_dir+batch))
            self.assertTrue(os.path.exists(self.output_root_dir+batch+'/samplesheet_batch'+str(batch_number)+'.csv'))
            self.assertTrue(os.path.exists(self.output_root_dir+batch+'/parameters_QC_batch'+str(batch_number)+'.csv'))
            self.assertTrue(os.path.exists(self.output_root_dir+batch+'/parameters_genotyping_batch'+str(batch_number)+'.csv'))
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

        self.assertTrue(os.path.exists(self.output_root_dir+'fastq_downloads'))
        self.assertTrue(os.path.exists(self.output_root_dir+'samples_per_batch.tsv'))
        with open(self.output_root_dir+'samples_per_batch.tsv') as input_file:
            self.assertEqual(input_file.readline(),'batch0\tbatch1\n', 'Header samples_per_batch.tsv not correct')
            line1 = input_file.readline()
            samples_line1 = line1.strip().split('\t')
            self.assertTrue('DRR000897' in samples_line1, 'DRR000897 not on line 1')
            self.assertTrue('DRR001173' in samples_line1, 'DRR001173 not on line 2')
            self.assertEqual(len(samples_line1), 2, 'Not 2 samples on line 1')
            line2 = input_file.readline()
            samples_line2 = line2.strip().split('\t')
            self.assertTrue('DRR001622' in samples_line2, 'DRR001622 not on line 2')
            self.assertEqual(len(samples_line2), 1, 'Not 1 sample on line 2')
        
        
        self.fail('Finish the test!') 

if __name__ == '__main__':  
    unittest.main(warnings='ignore')  

