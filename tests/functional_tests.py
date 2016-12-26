from .context import genotypePublicData
import requests

# Get the Homo Sapien samples (tax 9606). Change for samples of different organism
tax = '9606'
# Get the RNA-seq samples
library_strategy = 'RNA-seq'


url = 'http://www.ebi.ac.uk/ena/data/warehouse/search?query=%22tax_eq('+tax+')%20AND%20library_strategy=%22'+library_strategy+'%22%22&domain=read'

# Dr. Gene Tica wants to get genotypes for all the latest RNAseq samples available on ENA (http://www.ebi.ac.uk/ena/)
# To do this Gene needs to be able to download the FastQ files for all samples currently available
response = requests.get(url)

# The information Gene gets includes the link to the fastq file to download and the md5sum for checking validity of Fastq file
# along with several other fields


# Using the link to the fastq file the files are automatically downloaded to the provided outfolder
