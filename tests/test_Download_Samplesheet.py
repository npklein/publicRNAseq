from context import genotypePublicData
import os
import unittest
import shutil
import re

class Download_SamplesheetTest(unittest.TestCase):  
    def setUp(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_root_dir = self.script_dir+'/test_output/'
        if os.path.exists(self.output_root_dir):
            shutil.rmtree(self.output_root_dir)
        os.mkdir(self.output_root_dir)

    def tearDown(self):
        pass

    def test_download_samplesheet(self):
        # Get the Homo Sapien samples (tax 9606). Change for samples of different organism
        tax_id = '9606'
        # Get the RNA-seq samples
        library_strategy = 'RNA-Seq'
        first_public = '2010-02-26'
        download_ena_samplesheet = genotypePublicData.Download_ENA_samplesheet(tax_id, library_strategy, first_public)
#        download_ena_samplesheet.set_x11(True)
        # Dr. Gene Tica wants to get genotypes for all the latest RNAseq samples available on ENA (http://www.ebi.ac.uk/ena/)
        # To do this Gene needs to be able to download the FastQ files for all samples currently available
        download_ena_samplesheet.start(self.output_root_dir)

        # The location of the samplesheet needs to be retrievable
        ena_samplesheet = download_ena_samplesheet.get_samplesheet_file()
        pattern = '.*ena_'+tax_id+'_'+library_strategy+'_'+first_public+'_d\d{2}m\d{2}y\d{4}_h\d{2}m\d{2}s\d{2}.txt'
        self.assertTrue(bool(re.match(pattern,ena_samplesheet)), 'samplesheet name not following correct format')
        with open(ena_samplesheet) as input_file:
            header_columns = input_file.readline().split('\t')
            self.assertEqual(len(header_columns), 49, 'Not enough or too many header columns in samplesheet')
             
        self.assertTrue(os.path.exists(ena_samplesheet))


if __name__ == '__main__':  
    unittest.main(warnings='ignore')  
