from context import genotypePublicData
import os
import unittest
import shutil

class UtilsTest(unittest.TestCase):  
    def setUp(self):
        self.script_dir = os.path.normpath(os.path.dirname(os.path.abspath(__file__))+'/')
        self.output_root_dir = os.path.normpath(self.script_dir+'/test_output/')
        shutil.rmtree(self.output_root_dir)
        os.mkdir(self.output_root_dir)

    def tearDown(self):
        pass

    def test_can_change_directories(self):
        current_path_old = os.path.normpath(os.getcwd())
        # test after with statement the working directory is changed back again
        with genotypePublicData.Utils.cd(self.output_root_dir):
            current_path = os.path.normpath(os.getcwd())
            self.assertTrue(current_path == self.output_root_dir)
        current_path = os.path.normpath(os.getcwd())
        self.assertTrue(current_path == current_path_old)

    def test_get_all_indices(self):
        example_list = ['a','b','c']
        indices_expected = {'a':0,'b':1,'c':2}
        indices_result = genotypePublicData.Utils.get_all_indices(example_list)
        self.assertDictEqual(indices_expected,indices_result)
        
if __name__ == '__main__':  
    unittest.main(warnings='ignore')  

