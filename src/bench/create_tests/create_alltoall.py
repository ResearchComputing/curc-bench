#!/curc/admin/benchmarks/bin/python
#from django.conf import settings
from django import template
#if not settings.configured:
#    settings.configure()

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

HPL_TEMPLATE = """\
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
{{n}}
{% spaceless %}
{% for x in node_list %}{{x}}
{% endfor %}
{% endspaceless %}
EOF

. /curc/tools/utils/dkinit
use .openmpi-1.6.2_intel-13.0.0_torque-2.5.11_ib

echo '{{set_list}}' > data
mpirun /home/molu8455/admin/benchmarks/software/mpi/osu_alltoall  -f >> data

{% if set_0_list %}
echo '{{set_0_list}}' > data_pair_{{set_0_name}}
mpirun --host {{set_0_list}} /home/molu8455/admin/benchmarks/software/mpi/osu_alltoall  -f >> data_pair_{{set_0_name}} &
{% endif %}

{% if set_2_list %}
echo '{{set_2_list}}' > data_pair_{{set_2_name}}
mpirun --host {{set_2_list}} /home/molu8455/admin/benchmarks/software/mpi/osu_alltoall  -f >> data_pair_{{set_2_name}} &
{% endif %}

{% if set_4_list %}
echo '{{set_4_list}}' > data_pair_{{set_4_name}}
mpirun --host {{set_4_list}} /home/molu8455/admin/benchmarks/software/mpi/osu_alltoall  -f >> data_pair_{{set_4_name}} &
{% endif %}

{% if set_6_list %}
echo '{{set_6_list}}' > data_pair_{{set_6_name}}
mpirun --host {{set_6_list}} /home/molu8455/admin/benchmarks/software/mpi/osu_alltoall  -f >> data_pair_{{set_6_name}} &
{% endif %}

{% if set_8_list %}
echo '{{set_8_list}}' > data_pair_{{set_8_name}}
mpirun --host {{set_8_list}} /home/molu8455/admin/benchmarks/software/mpi/osu_alltoall  -f >> data_pair_{{set_8_name}} &
{% endif %}

{% if set_10_list %}
echo '{{set_10_list}}' > data_pair_{{set_10_name}}
mpirun --host {{set_10_list}} /home/molu8455/admin/benchmarks/software/mpi/osu_alltoall  -f >> data_pair_{{set_10_name}} &
{% endif %}

{% if set_12_list %}
echo '{{set_12_list}}' > data_pair_{{set_12_name}}
mpirun --host {{set_12_list}} /home/molu8455/admin/benchmarks/software/mpi/osu_alltoall  -f >> data_pair_{{set_12_name}} &
{% endif %}

{% if set_14_list %}
echo '{{set_14_list}}' > data_pair_{{set_14_name}}
mpirun --host {{set_14_list}} /home/molu8455/admin/benchmarks/software/mpi/osu_alltoall  -f >> data_pair_{{set_14_name}} &
{% endif %}

{% if set_16_list %}
echo '{{set_16_list}}' > data_pair_{{set_16_name}}
mpirun --host {{set_16_list}} /home/molu8455/admin/benchmarks/software/mpi/osu_alltoall  -f >> data_pair_{{set_16_name}} &
{% endif %}

{% if set_18_list %}
echo '{{set_18_list}}' > data_pair_{{set_18_name}}
mpirun --host {{set_18_list}} /home/molu8455/admin/benchmarks/software/mpi/osu_alltoall  -f >> data_pair_{{set_18_name}} &
{% endif %}

wait

{% if set_last_list %}
echo '{{set_last_list}}' > data_pair_{{set_last_name}}
mpirun --host {{set_last_list}} /home/molu8455/admin/benchmarks/software/mpi/osu_alltoall  -f >> data_pair_{{set_last_name}}
{% endif %}

{% spaceless %}
{% for x in node_list %}
echo {{x}} > data_single_{{x}}
mpirun --host {{x}} /home/molu8455/admin/benchmarks/software/mpi/osu_alltoall  -f >> data_single_{{x}} &
{% endfor %}
{% endspaceless %}

wait
"""

RACK_TEMPLATE = """\
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
{{n}}
{% spaceless %}
{% for x in node_list %}{{x}}
{% endfor %}
{% endspaceless %}
EOF

. /curc/tools/utils/dkinit
use .openmpi-1.6.2_intel-13.0.0_torque-2.5.11_ib

echo '{{set_list}}' > data
mpirun -mca coll_tuned_use_dynamic_rules 1 -mca coll_tuned_alltoallv_algorithm 2 /home/molu8455/admin/benchmarks/software/mpi/osu_ata_rack  -f >> data

"""
# These are parameters for the script
#==============================================================================
def processors_per_node():
    return 12

def create_pbs_template(mypath, hpl):
    output_file = os.path.join(mypath,"script_" + hpl['job_name'] + "-" + hpl['id'])
    file_out = open(output_file,'w')
    t = template.Template(HPL_TEMPLATE)
    contents = t.render(template.Context(hpl))
    file_out.write(contents)
    file_out.close()

def create_pbs_rack_template(mypath, hpl):
    output_file = os.path.join(mypath,"script_" + hpl['job_name'] + "-" + hpl['id'])
    file_out = open(output_file,'w')
    t = template.Template(RACK_TEMPLATE)
    contents = t.render(template.Context(hpl))
    file_out.write(contents)
    file_out.close()

def render(mypath, queue, node_list):
    n = len(node_list)
    logger.debug("number of nodes = " + str(n))
    hpl = {}

    hpl['queue'] = queue
    hpl['id'] = str(uuid.uuid1())
    #hpl['id'] = str(111)
    hpl['nodes'] = n
    hpl['processors'] = n*processors_per_node()
    hpl['node_list'] = node_list
    hpl['time_estimate'] = "00:20:00"

    # Max problem size?
    N = n
    hpl['n'] = N

    job_name = "alltoall-" + str(n)

    hpl['job_name'] = job_name
    hpl['set_list'] = node_string = "".join(["%s, " % n for n in node_list])

    infiniband.rack_subsets(hpl, node_list)
    if len(node_list) < 19:
        create_pbs_template(mypath, hpl)
    else:
        hpl['time_estimate'] = "01:00:00"
        create_pbs_rack_template(mypath, hpl)


def create(node_list, queue, path):
    #print node_list
    mypath = os.path.join(path,"alltoall")
    util.create_directory_structure(mypath)

    my_rack_path = os.path.join(path,"rack_alltoall")
    util.create_directory_structure(my_rack_path)

    # Test with 18 nodes on a switch
    logger.info("Creating 18 node alltoall tests")
    rack_switch = infiniband.rack_switch_18(node_list)
    rack_list = []
    for name, name_list in rack_switch.iteritems():
        #print name, name_list
        if len(name_list) > 0:
             render(mypath, queue, name_list)
             rack_list.extend(name_list)

    # Test with 18 nodes on a switch
    logger.info("Creating rack node alltoall tests")
    rack_switch = infiniband.rack(node_list)
    rack_list = []
    for name, name_list in rack_switch.iteritems():
        #print name, name_list
        if len(name_list) > 0:
             render(my_rack_path, queue, name_list)
             rack_list.extend(name_list)


    logger.debug("not tested "+ str(len(set(node_list).difference(set(rack_list)))))
