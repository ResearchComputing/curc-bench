from ez_setup import use_setuptools
use_setuptools()

import os
import setuptools

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setuptools.setup(
    name = "bench",
    version = "0.0.0",
    author = "Research Computing",
    author_email = "",
    description = ("HPC Benchmarking"),
    license = "BSD",
    keywords = "",
    url = "",
    package_dir = {'': 'src'},
    packages=['bench'],
    install_requires=['NumPy>=1.7.0','pandas>=0.7.3','requests>=0.14.1','cython>=0.21','Pysam>=0.5'],
    tests_require=['nose'],
    # test_suite="src/tests",
    long_description=read('README'),
    classifiers=[
        "License :: BSD License",
    ],
)
