from bench.util import util
from bench.util import infiniband
import fileinput
from jinja2 import Template
import json
import logging
import math
import os
import sys
import uuid


logger = logging.getLogger('Benchmarks')


HPL_TEMPLATE = """\
#!/bin/bash
#SBATCH -N {{num_nodes}}
#SBATCH --nodelist={% for x in node_list %}{{x}}{% if not loop.last %},{%endif%}{% endfor %}
#SBATCH --time=0:30:00
#SBATCH --reservation={{queue}}
#SBATCH --account=crcbenchmark
#SBATCH --qos=admin
#SBATCH --ntasks-per-node=12


mkdir -p test_{{id}}
cd test_{{id}}


cat >> info << EOF
{{id}}
{{n}}
{% filter trim %}
{% for x in node_list %}{{x}}
{% endfor %}
{% endfilter %}
EOF

module load openmpi/openmpi-1.6.4_intel-13.0.0_torque-4.1.4_ib

echo '{{set_list}}' > data
mpirun ./lib/osu-micro-benchmarks-3.8/mpi/collective/osu_alltoall  -f >> data
"""


def processors_per_node():
    return 12


def create_pbs_template(mypath, hpl):
    output_file = os.path.join(mypath,"script_" + hpl['job_name'])
    file_out = open(output_file,'w')
    t = Template(HPL_TEMPLATE)
    contents = t.render(**hpl)
    file_out.write(contents)
    file_out.close()


def create_pbs_rack_template(mypath, hpl):
    output_file = os.path.join(mypath,"script_" + hpl['job_name'] + "-" + hpl['id'])
    file_out = open(output_file,'w')
    t = Template(RACK_TEMPLATE)
    contents = t.render(**hpl)
    file_out.write(contents)
    file_out.close()


def render(mypath, queue, node_list, name):
    n = len(node_list)
    logger.debug("number of nodes = " + str(n))
    hpl = {}

    hpl['queue'] = queue
    hpl['id'] = name
    hpl['nodes'] = n
    hpl['processors'] = n*processors_per_node()
    hpl['node_list'] = node_list
    hpl['num_nodes'] = len(node_list)
    hpl['time_estimate'] = "00:30:00"

    N = n
    hpl['n'] = N
    hpl['job_name'] = name
    hpl['set_list'] = node_string = "".join(["%s, " % n for n in node_list])
    create_pbs_template(mypath, hpl)


def create(node_list, queue, path, allrack, allswitch, allpair):

    if allrack==True:
      mypath = os.path.join(path,"alltoall_rack")
      util.create_directory_structure(mypath)

      logger.info("Creating rack alltoall tests")
      test = infiniband.rack(node_list)

      for name, name_list in test.iteritems():
          if len(name_list) > 0:
              render(mypath, queue, name_list, name)

    if allswitch==True:
      mypath = os.path.join(path,"alltoall_switch")
      util.create_directory_structure(mypath)

      logger.info("Creating switch alltoall tests")
      test = infiniband.rack_switch_18(node_list)
      for name, name_list in test.iteritems():
          if len(name_list) > 0:
              render(mypath, queue, name_list, name)

    if allpair==True:
      mypath = os.path.join(path,"alltoall_pair")
      util.create_directory_structure(mypath)

      logger.info("Creating pair alltoall tests")

      test = infiniband.rack_switch_pairs(node_list)
      for name, name_list in test.iteritems():
          if len(name_list) > 0:
              render(mypath, queue, name_list, name)
