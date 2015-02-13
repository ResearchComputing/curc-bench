#!/curc/admin/benchmarks/bin/python

from jinja2 import Template

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

# . /curc/tools/utils/dkinit
# use .openmpi-1.6.2_intel-13.0.0_torque-2.5.11_ib

module load openmpi/openmpi-1.6.4_intel-13.0.0_torque-4.1.4_ib

echo '{{set_list}}' > data
mpirun /home/molu8455/admin/benchmarks/software/mpi/osu_alltoall  -f >> data

#nds=$((`cat $PBS_NODEFILE | uniq | wc -l`*12))
#for (( c=12; c<=$nds; c+=12 ))
#do
#  echo "$c" >> data
#  mpirun -np $c /home/molu8455/admin/benchmarks/software/mpi/osu_alltoall_one  -f >> data
#done

"""

# These are parameters for the script
#==============================================================================
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
    #hpl['id'] = str(111)
    hpl['nodes'] = n
    hpl['processors'] = n*processors_per_node()
    hpl['node_list'] = node_list
    hpl['num_nodes'] = len(node_list)
    hpl['time_estimate'] = "00:30:00"

    # Max problem size?
    N = n
    hpl['n'] = N
    hpl['job_name'] = name
    hpl['set_list'] = node_string = "".join(["%s, " % n for n in node_list])
    #hpl['time_estimate'] = "01:00:00"
    create_pbs_template(mypath, hpl)


def create(node_list, queue, path, args):

    # create rack level tests
    if args.allrack==True:
      mypath = os.path.join(path,"alltoall_rack")
      util.create_directory_structure(mypath)

      logger.info("Creating rack alltoall tests")
      test = infiniband.rack(node_list)

      for name, name_list in test.iteritems():
          if len(name_list) > 0:
              #print name_list
              render(mypath, queue, name_list, name)

    # Rack switch level test
    if args.allswitch==True:
      mypath = os.path.join(path,"alltoall_switch")
      util.create_directory_structure(mypath)

      logger.info("Creating switch alltoall tests")
      test = infiniband.rack_switch_18(node_list)
      for name, name_list in test.iteritems():
          if len(name_list) > 0:
              render(mypath, queue, name_list, name)

    if args.allpair==True:
      mypath = os.path.join(path,"alltoall_pair")
      util.create_directory_structure(mypath)

      logger.info("Creating pair alltoall tests")

      test = infiniband.rack_switch_pairs(node_list)
      #print test
      for name, name_list in test.iteritems():
          if len(name_list) > 0:
              render(mypath, queue, name_list, name)





    # for name, name_list in test.iteritems():
    #     if len(name_list) > 0:
    #         #render(mypath, queue, name_list)
    #         print name
    #         for x in name_list:
    #             print x,
    #         print ''

    # #print node_list
  #   mypath = os.path.join(path,"alltoall")
  #   util.create_directory_structure(mypath)
  #
  #   my_rack_path = os.path.join(path,"rack_alltoall")
  #   util.create_directory_structure(my_rack_path)
  #
  #   # Test with 18 nodes on a switch
  #   logger.info("Creating 18 node alltoall tests")
  #   rack_switch = infiniband.rack_switch_18(node_list)
  #   rack_list = []
  #   for name, name_list in rack_switch.iteritems():
  #       #print name, name_list
  #       if len(name_list) > 0:
  #            render(mypath, queue, name_list)
  #            rack_list.extend(name_list)
  #
  #   # Test with 18 nodes on a switch
  #   logger.info("Creating rack node alltoall tests")
  #   rack_switch = infiniband.rack(node_list)
  #   rack_list = []
  #   for name, name_list in rack_switch.iteritems():
  #       #print name, name_list
  #       if len(name_list) > 0:
  #            render(my_rack_path, queue, name_list)
  #            rack_list.extend(name_list)


    #logger.debug("not tested "+ str(len(set(node_list).difference(set(rack_list)))))
