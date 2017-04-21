from context import genotypePublicData
import os
import unittest
import shutil

class SamplesheetsTest(unittest.TestCase):  
    def setUp(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))+'/'
        # Samplesheets class is used to make and maintain compute samplesheets
        self.output_root_dir = self.script_dir+'test_output/'
        self.project = 'test'
        shutil.rmtree(self.output_root_dir)
        os.mkdir(self.output_root_dir)

    def tearDown(self):
        pass

    def test_can_read_in_samplesheet_and_make_batches(self):  
        batches = [{'DRR000897': ['DRR000897.fastq.gz'], 'DRR001173': ['DRR001173.fastq.gz']}, {'DRR001622': ['DRR001622_1.fastq.gz', 'DRR001622_2.fastq.gz']}]
        compute = genotypePublicData.Compute(batches=batches, root_dir=self.output_root_dir, project=self.project)
        
        # github clone the molgenis pipelines
        compute.get_molgenis_pipelines()
        self.assertTrue(os.path.exists(self.output_root_dir+'molgenis-pipelines/'))
        
        # create parameter files
        compute.create_parameter_files(self.script_dir+'/../configurations/')
        
        # create samplesheet
        compute.create_QC_samplesheet()
        
        #create scripts
        compute.create_molgenis_generate_jobs_script(self.compute_version)
        
        #generate jobs
        compute.generate_jobs()

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
        
        
        

if __name__ == '__main__':  
    unittest.main(warnings='ignore')  

