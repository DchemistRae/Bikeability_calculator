from setuptools import setup, find_packages


with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name= 'bikeability',
    version= '0.0.1',
    description= 'An automated bikeabililty assessment tool.',
    long_description= long_description,
    long_description_content_type= 'text/markdown',
    py_modules= ['bikeability'],
    package_dir={'':'src'},
    classifiers = [
    'Intended Audience :: Researchers',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.7'],
    url='https://github.com/DchemistRae/Bikeability_calculator',
    author='Raymond Asimhi',
    author_email='rasimhi@gmx.de',
    install_requires = ['tqdm ~= 4.62.3', 'shapely ~=1.7.1', 'osmnx ~=1.1.1']
)   