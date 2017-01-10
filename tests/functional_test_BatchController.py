from context import genotypePublicData
import os
import unittest
import shutil

class BatchControlTest(unittest.TestCase):  
    def setUp(self):
        # Control Batches can be used to run the whole pipeline and divide the samples up in multiple batches for processing
        # Download starts per batch sequentially, then all jobs from that batch are submitted using Molgenis Compute, and then
        # the next batch starts downloading
        self.ena_samplesheet = 'test_data/ena_example_samplesheet.txt'
        self.output_root_dir = 'test_output/'
        self.project = 'test'
        shutil.rmtree(self.output_root_dir)
        os.mkdir(self.output_root_dir)

    def tearDown(self):
        pass

    def test_can_read_in_samplesheet_and_make_batches(self):  
        # some samples need to be included from the samplesheet
        include_list = ['DRR000897','DRR001173','DRR001174','DRR001485']
        # some samples need to be excluded
        exclude_list = ['DRR001485']
        batch_controller = genotypePublicData.BatchController(self.ena_samplesheet, samples_per_batch=2, project=self.project, 
                                                              inclusion_list=include_list, exclusion_list=exclude_list)
        # We can get the created batches from batch_controller 
        batches = batch_controller.get_batches()
        # The batch controller should contain 2 batches, one with 2 samples and one with 1 sample
        self.assertEqual(len(batches), 2, 'Does not contain 2 batches')
        self.assertEqual(batches, [['DRR000897','DRR001173'],['DRR001174']], 'Batch list not the same')
                
        # We want to set up the project first by creating the directory structure necesarry for putting jobs and results in
        batch_controller.setup_project(self.output_root_dir)
        for batch in range(0, len(batches),1):
            self.assertTrue(os.path.exists(self.output_root_dir+'/batch'+str(batch)))
        self.assertTrue(os.path.exists(self.output_root_dir+'fastq_downloads'))
        self.assertTrue(os.path.exists(self.output_root_dir+'samples_per_batch.tsv'))
        with open(self.output_root_dir+'samples_per_batch.tsv') as input_file:
            self.assertEqual(input_file.readline(),'batch0\tbatch1\n', 'Header samples_per_batch.tsv not correct')
            self.assertEqual(input_file.readline(),'DRR000897\tDRR001174\n', 'First line samples_per_batch.tsv not correct')
            self.assertEqual(input_file.readline(),'DRR001173\n', 'First line samples_per_batch.tsv not correct')
        self.fail('Finish the test!') 

if __name__ == '__main__':  
    unittest.main(warnings='ignore')  

