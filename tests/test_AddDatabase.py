from context import genotypePublicData
import os
import unittest
import shutil
from RNAseqParser import molgenis_wrapper

class AddDatabaseTest(unittest.TestCase):  
    def setUp(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))+'/'

        self.ena_samplesheet = self.script_dir+'test_data/ena_example_samplesheet.txt'
        self.output_root_dir = self.script_dir+'test_output/'
        self.project = 'test'
        shutil.rmtree(self.output_root_dir)
        os.mkdir(self.output_root_dir)
        include_list = ['small.fastq.gz']
        # folder structure is created when initializing
        self.batch_controller = genotypePublicData.BatchController(self.ena_samplesheet, project=self.project, 
                                                              root_dir=self.output_root_dir,inclusion_list=include_list)
        # setup project by generating samplesheets, parameter files etc
        self.batch_controller.setup_project(echo_output=False)

    def tearDown(self):
        pass
        
    def test_can_add_job_info_to_database(self):
        '''Download the samples one batch at a time'''
        self.batch_controller.submit_QC_batch(0)
        # make a connection to the molgenis database. This connection will be passed to the other functions
        with molgenis_wrapper.Connect_Molgenis('http://molgenis39.target.rug.nl/') as connection:
            pass
        self.fail('Finish the test!')

if __name__ == '__main__':  
    unittest.main(warnings='ignore')  

