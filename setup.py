from ez_setup import use_setuptools
use_setuptools()

import multiprocessing
import os
import setuptools
import subprocess


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def git_describe():
    git_describe = subprocess.Popen(['git', 'describe', '--tags'], stdout=subprocess.PIPE)
    stdout, _ = git_describe.communicate()
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
        packages=['bench'],
        install_requires=['argparse', 'jinja2', 'python-hostlist', 'pyslurm'],
        dependency_links=['http://github.com/PySlurm/pyslurm/tarball/16.05.5#egg=pyslurm'],
        tests_require=['nose', 'importlib', 'mock'],
        test_suite = 'nose.collector',
        long_description=read('README.mdwn'),
        classifiers=[
            'License :: BSD License',
        ],
        entry_points={
            'console_scripts': [
                'bench = bench.cli:main',
            ],
        },
        package_data={
            'bench.tests': ['*.job'],
        },
    )


if __name__ == '__main__':
    main()
