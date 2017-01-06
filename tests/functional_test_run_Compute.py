from context import genotypePublicData
import os

# With the downloaded samples (from functional_test_Download_Samples_<aspera/ftp>.py) Gene wants to run the Molgenis pipeline per batch of 2

# The samplesheet he gets includes the link to the fastq file to download and the md5sum for checking validity of Fastq file
ena_samplesheet = 'test_data/ena_example_samplesheet.txt'
jobs_folder = '/tmp/jobs/'
molgenis_compute_location = 'molgenis_compute.sh'
run_compute = genotypePublicData.Run_Compute(molgenis_compute_location,ena_samplesheet,jobs_folder,batch=2)

include_list = ['DRR000897','DRR001173','DRR001174']
exclude_list = ['DRR001174']
run_compute.set_include_list(include_list)
run_compute.set_exclude_list(exclude_list)
# Using the link to the fastq file the files are automatically downloaded to the provided outfolder using aspera
run_compute.make_jobs()
