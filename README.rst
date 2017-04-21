Automatically download samples from ENA and process them through the Molgenis Compute pipeline for RNAseq genotyping.

Needs Python 3 (tested with 3.5.2)

To install, do 

    pip install -r requirements.txt
    python setup.py install 


To download the current RNA-seq samplesheet to your /tmp directory

    import genotypePublicData
    # Get the Homo Sapien samples (tax 9606). Change for samples of different organism
    tax = '9606'
    # Get the RNA-seq samples
    library_strategy = 'RNA-seq'
    download_ena_samples = genotypePublicData.Download_ENA_samplesheet(tax, library_strategy)
    download_ena_samples.download_samplesheet('/tmp')
