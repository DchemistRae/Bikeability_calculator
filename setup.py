import os
from setuptools import setup, find_packages

# Read long description
with open('README.md', 'r') as fh:
    long_description = fh.read()

# only specify install_requires if not in RTD environment
if os.getenv("READTHEDOCS") == "True":
    INSTALL_REQUIRES = []
else:
    with open("requirements.txt") as f:
        INSTALL_REQUIRES = [line.strip() for line in f.readlines()]

setup(
    name= 'bikeability',
    version= '0.0.1',
    description= 'An automated bikeabililty assessment tool.',
    long_description= long_description,
    long_description_content_type= 'text/markdown',
    #py_modules= ['bikeability'],
    #package_dir={'':'src'},
    classifiers = [
    'Intended Audience :: Researchers/ SCience',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.7'],
    url='https://github.com/DchemistRae/Bikeability_calculator',
    author='Raymond Asimhi',
    author_email='rasimhi@gmx.de',
    packages= ['bikeability'],
    install_requires='INSTALL_REQUIRES',
)   