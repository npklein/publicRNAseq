from context import genotypePublicData

# Gene has used functional_test_Download_Samplesheet.py to downlaod the samplesheet from ENA
# The samplesheet he gets includes the link to the fastq file to download and the md5sum for checking validity of Fastq file
# along with several other information fields
# Using this information he wants to download the FastQ samples and check their md5sum. However, Gene is only interested
# in a select few samples so some samples have to be included and excluded
# if code from functional_test_DownloadSamplesheet is run can use download_ena_samplesheet.get_samplesheet_file() instead
ena_samplesheet = 'test_data/ena_example_samplesheet.txt'
download_ena_samples = genotypePublicData.Download_ENA_samples(ena_samplesheet)

include_list = ['DRR000897','DRR001173','DRR001174']
exclude_list = ['DRR001174']
download_ena_samples.set_include_list(include_list)
download_ena_samples.set_exclude_list(exclude_list)
# Using the link to the fastq file the files are automatically downloaded to the provided outfolder using ftp
download_ena_samples.download_samples(download_protocol='ftp')

# or faster, using aspera
download_ena_samples.download_samples()
