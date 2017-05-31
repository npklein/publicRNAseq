from context import genotypePublicData
import os
import unittest
import shutil

class CleanupTest(unittest.TestCase):  
    def setUp(self):
        pass

    def tearDown(self):
        pass
        
    def test_can_add_job_info_to_database(self):
        '''Download the samples one batch at a time'''
        self.batch_controller.submit_QC_batch(0)
        cleaner = genotypePublicData.Cleanup()
        cleanup.clean()
        
if __name__ == '__main__':  
    unittest.main(warnings='ignore')  

