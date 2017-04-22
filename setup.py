#!/usr/bin/env python

from setuptools import setup

setup(name='genotypePublicData',
      version='0.0.2',
      description='Download and genotype RNAseq samples from ENA',
      author='Niek de Klein',
      author_email='niekdeklein@gmail.com',
      url='https://github.com/npklein/publicRNAseq',
      license="?",
      packages=['genotypePublicData'],
      classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3'
      ],
    keywords='genotyping RNAseq ENA',
    install_requires=['selenium',
                      'requests',
                      'xvfbwrapper',
                      'pyvirtualdisplay',
                      'GitPython'],
    package_data={'configurations':['*']},
    test_suite='nose.collector',
    tests_require=['nose'],
     )
