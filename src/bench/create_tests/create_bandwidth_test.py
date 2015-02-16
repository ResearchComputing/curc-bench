#!/curc/admin/benchmarks/bin/python

import os
import sys
import shutil

from jinja2 import Template

from bench.util import infiniband


from bench.util import util
import logging
logger = logging.getLogger('Benchmarks')

PBS_TEMPLATE = """\
#!/bin/bash
#SBATCH -N 2
#SBATCH --nodelist={{node_list}}
#SBATCH --time=0:45:00
#SBATCH --reservation={{queue_name}}
#SBATCH --account=crcbenchmark
#SBATCH --qos=admin
#SBATCH --ntasks-per-node=1

module load openmpi/openmpi-1.6.4_intel-13.0.0_torque-4.1.4_ib

mkdir -p {{job_name}}
cd {{job_name}}

mpirun -np 2 /home/molu8455/projects/redhat_6/software/bandwidth/osu_bw > data_bw
# mpirun -pernode /home/molu8455/projects/software/cbench/cbench-1.2.2/bin/osu_bw > data_bw
# mpirun -pernode /home/molu8455/projects/software/cbench/cbench-1.2.2/bin/osu_latency > data_latency
# mpirun -pernode /home/molu8455/projects/software/cbench/cbench-1.2.2/bin/stress | grep aggregate > data_stress
# mpirun -pernode /home/molu8455/projects/software/cbench/cbench-1.2.2/bin/mpi_latency > data_mpi_latency
# mpirun -pernode /home/molu8455/projects/software/cbench/cbench-1.2.2/bin/osu_bcast > data_bcast
#
# mpirun -pernode /home/molu8455/projects/software/cbench/cbench-1.2.2/bin/osu_bw > data_bw
# mpirun -pernode /home/molu8455/projects/software/cbench/cbench-1.2.2/bin/osu_latency > data_latency



"""



def create_node_pairs(node_list):
    pair_list = []

    odd_list = node_list[::2]
    even_list = node_list[1::2]

    tmp1 = odd_list[0]
    if len(odd_list) > len(even_list):
        tmp1 = odd_list.pop(len(odd_list)-1)

    # create list
    for i in range(len(odd_list)):
        node_pair = odd_list[i], even_list[i]
        node_pair = sorted(node_pair)
        if node_pair not in pair_list:
            pair_list.append(node_pair)

    # create second list
    odd_list.append(tmp1)
    tmp2 = odd_list.pop(0)

    for i in range(len(odd_list)):
        node_pair = odd_list[i], even_list[i]
        node_pair = sorted(node_pair)
        if node_pair not in pair_list:
            pair_list.append(node_pair)

    # add the last pair if odd size list
    if tmp1 != tmp2:
        node_pair = tmp1, tmp2
        node_pair = sorted(node_pair)
        pair_list.append(node_pair)

    return sorted(pair_list)

def create_pbs_template(values, mypath):
    output_file = os.path.join(mypath,"script_" + values['job_name'])
    file_out = open(output_file,'w')
    t = Template(PBS_TEMPLATE)
    contents = t.render(**values)
    file_out.write(contents)
    file_out.close()

def render(mypath,queue,pair):
    #print pair
    node_list = pair[0] + ":ppn=12+" + pair[1] + ":ppn=12"
    node_list = pair[0] + ',' +pair[1]
    job_name = pair[0] + "-" + pair[1]
    values = {}
    values['job_name'] = job_name
    values['queue_name'] = queue
    values['node_list'] = node_list
    create_pbs_template(values, mypath)

def create(node_list, queue, current_path):

    #print 'here'
    mypath = os.path.join(current_path,"bandwidth")
    util.create_directory_structure(mypath)

    #logger.info("Creating switch alltoall tests")
    test = infiniband.rack_switch_18(node_list)
    for name, name_list in test.iteritems():
      if len(name_list) > 0:
          #print name_list
          pass
          #render(mypath, queue, name_list, name)


    rack_switch = infiniband.rack_switch_18(node_list)
    #print node_list, rack_switch
    rack_list = []
    for name, name_list in rack_switch.iteritems():
        #print name, name_list
        if len(name_list) > 0:
            #rack_list.extend(name_list)
            data = infiniband.rack_list_subsets(name_list)
            #print "here", data
            for j,k in data.iteritems():
                #print k
                render(mypath, queue, k)

    logger.debug("not tested "+ str(len(set(node_list).difference(set(rack_list)))))
