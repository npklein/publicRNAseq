from context import genotypePublicData
import os
# Get the Homo Sapien samples (tax 9606). Change for samples of different organism
tax = '9606'
# Get the RNA-seq samples
library_strategy = 'RNA-seq'

download_ena_samplesheet = genotypePublicData.Download_ENA_samplesheet(tax, library_strategy)

# Dr. Gene Tica wants to get genotypes for all the latest RNAseq samples available on ENA (http://www.ebi.ac.uk/ena/)
# To do this Gene needs to be able to download the FastQ files for all samples currently available
download_ena_samplesheet.download_samplesheet('/tmp')

# The location of the samplesheet needs to be retrievable
ene_samplesheet = download_ena_samplesheet.get_samplesheet_file()

assert os.path.exists(ena_samplesheet)