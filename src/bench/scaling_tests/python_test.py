# from django import template

import fileinput, os, sys
import math
import numpy
from scipy import stats
import uuid
import json

from bench.util import util
from bench.util import infiniband

import logging
logger = logging.getLogger('Benchmarks')

SCALING_TEMPLATE = """\
#!/bin/bash
#PBS -N job.{{id}}
#PBS -q {{queue}}
#PBS -l walltime={{time_estimate}}
#PBS -l nodes={% for x in node_list %}{{x}}:ppn=12{% if not forloop.last %}+{%endif%}{% endfor %}
#PBS -j oe

cd $PBS_O_WORKDIR

mkdir -p test_{{id}}
cd test_{{id}}


cat >> info << EOF
{{id}}
{{nodes}}
{% spaceless %}
{% for x in node_list %}{{x}}
{% endfor %}
{% endspaceless %}
EOF

. /curc/tools/utils/dkinit
reuse .mpi4py-3.1_openmpi-1.6.3_gcc-4.7.2_torque-2.5.11_ib

mpirun python /home/molu8455/projects/python_hpc/mpi4py_examples/osu_alltoall.py  -f >> data_python_alltoall

"""

def create_pbs_template(mypath, data):
    output_file = os.path.join(mypath,"script_" + data['job_name'] + "-" + data['id'])
    file_out = open(output_file,'w')
    t = template.Template(SCALING_TEMPLATE)
    contents = t.render(template.Context(data))
    file_out.write(contents)
    file_out.close()

def render(mypath, node_list):
    data = {}
    data['time_estimate'] = "01:00:00"

    n = len(node_list)
    logger.debug("number of nodes = " + str(n))
    data['id'] = str(uuid.uuid1())
    data['nodes'] = n
    data['processors'] = n*12
    data['node_list'] = node_list
    job_name = "python-alltoall-" + str(n)
    data['job_name'] = job_name

    create_pbs_template(mypath, data)
