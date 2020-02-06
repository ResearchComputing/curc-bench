import unittest
import os
import setuptools
import subprocess


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def get_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    return test_suite

def git_describe():
    stdout = subprocess.getoutput('git describe --tags')
    return stdout.strip()

def main ():
    setuptools.setup(
        name = 'bench',
        version = git_describe(),
        author = 'Research Computing',
        author_email = '',
        description = ('HPC Benchmarking'),
        license = 'BSD',
        keywords = '',
        url = '',
        package_dir = {'': 'src'},
        packages=['bench', 'bench.conf', 'bench.tests'],
        include_package_data=True,
        install_requires=['argparse', 'jinja2>=2.10,<3', 'python-hostlist>=1.20,<=2', 'pyslurm>17.10,<=18', 'tabulate<=1',
            'datetime>=4.3,<=5'],
        dependency_links=['http://github.com/PySlurm/pyslurm/tarball/19.05.0#egg=pyslurm'],
        tests_require=['importlib'],
        test_suite = 'setup.get_test_suite',
        long_description=read('README.mdwn'),
        classifiers=[
            'License :: BSD License',
        ],
        entry_points={
            'console_scripts': [
                'bench = bench.driver:driver',
            ],
        },
    )


if __name__ == '__main__':
    main()
