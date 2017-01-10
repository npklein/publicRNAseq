from context import genotypePublicData
import unittest
import shutil
import os

class Download_SamplesTest(unittest.TestCase):
    # Gene has used functional_test_Download_Samplesheet.py to downlaod the samplesheet from ENA
    # The samplesheet he gets includes the link to the fastq file to download and the md5sum for checking validity of Fastq file
    # along with several other information fields
    # Using this information he wants to download the FastQ samples and check their md5sum. However, Gene is only interested
    # in a select few samples so some samples have to be included and excluded
    # if code from functional_test_DownloadSamplesheet is run can use download_ena_samplesheet.get_samplesheet_file() instead  
    def setUp(self):
        self.output_root_dir = 'test_output/'
        if os.path.exists(self.output_root_dir):
            shutil.rmtree(self.output_root_dir)
        os.mkdir(self.output_root_dir)
        self.download_protocol = 'ftp' # other option is aspera

    def tearDown(self):
        pass

    def test_download_samples(self):
        ena_samplesheet = 'test_data/ena_example_samplesheet.txt'
        download_ena_samples = genotypePublicData.Download_ENA_samples(ena_samplesheet, self.output_root_dir, aspera_openssh='~/.aspera/connect/etc/asperaweb_id_dsa.openssh')

        include_list = ['DRR000897','DRR001173','DRR001174','DRR001622']
        exclude_list = ['DRR001174']
        download_ena_samples.set_include_list(include_list)
        download_ena_samples.set_exclude_list(exclude_list)
        # Using the link to the fastq file the files are automatically downloaded to the provided outfolder using aspera
        download_ena_samples.download_samples(download_protocol=self.download_protocol)


if __name__ == '__main__':  
    unittest.main(warnings='ignore')  