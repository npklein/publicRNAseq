from context import genotypePublicData
import requests

# Get the Homo Sapien samples (tax 9606). Change for samples of different organism
tax = '9606'
# Get the RNA-seq samples
library_strategy = 'RNA-seq'

download_ena_samples = genotypePublicData.Download_ENA_samplesheet(tax, library_strategy)

# Dr. Gene Tica wants to get genotypes for all the latest RNAseq samples available on ENA (http://www.ebi.ac.uk/ena/)
# To do this Gene needs to be able to download the FastQ files for all samples currently available
download_ena_samples.download_samplesheet('ENA')

# The information Gene gets includes the link to the fastq file to download and the md5sum for checking validity of Fastq file
# along with several other fields
ass

# Using the link to the fastq file the files are automatically downloaded to the provided outfolder
