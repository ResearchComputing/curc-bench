#!/usr/bin/env python
import argparse

import os
import sys
import shutil

from django.conf import settings
from django import template
if not settings.configured:
    settings.configure()


from util import read_node_list, categorize,  create_directory_structure

PBS_TEMPLATE = """\
#!/bin/bash
#PBS -N output.{{job_name}}
#PBS -q {{queue_name}}
#PBS -l walltime=00:10:00
#PBS -l nodes=2:ppn=12
#PBS -j oe

. /curc/tools/utils/dkinit

use Torque
use Moab
use {{dotkit}}

cd $PBS_O_WORKDIR
mkdir -p {{job_name}}
cd {{job_name}}

cp /home/molu8455/projects/software/cbench/cbench-1.2.2/opensource/osutests/osu_bw.c .
mpicc osu_bw.c -o osu_bw
chmod 755 osu_bw
mpirun -pernode osu_bw > data_bw

"""

def create_directory_structure(dir_name):
    
    if os.path.exists(dir_name):
        pass
    else:
        try:
            os.mkdir(dir_name)
        except os.error as e:
            print "ERROR: " + e.strerror

def create_pbs_template(values, mypath):
    output_file = os.path.join(mypath,"script_" + values['job_name'])
    file_out = open(output_file,'w')
    t = template.Template(PBS_TEMPLATE)
    contents = t.render(template.Context(values))
    file_out.write(contents)
    file_out.close()    
 
def create(dotkit):
    
    print dotkit
    current_path = os.getcwd()
    mypath = os.path.join(current_path,"mpi_test")
    create_directory_structure(mypath)
    job_name = "mpi_test"+dotkit
    values = {}
    values['job_name'] = job_name
    values['queue_name'] = "janus-admin"
    values['dotkit'] = dotkit
    create_pbs_template(values, mypath)
    
#==============================================================================  
if __name__ == '__main__':  
    
    parser = argparse.ArgumentParser()            
    parser.add_argument('-d','--dotkit', help='MPI dotkit', dest='dotkit')
    
    args = parser.parse_args()
    
    create(args.dotkit)


