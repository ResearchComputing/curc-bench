#!/usr/bin/env python

import os
import sys
import shutil

from jinja2 import Template

from bench.util import util

NODE_TEMPLATE = """\
#!/bin/bash
#SBATCH -N 1
#SBATCH --nodelist={{node_name}}
#SBATCH --time=0:45:00
#SBATCH --reservation={{queue_name}}
#SBATCH --account=crcbenchmark
#SBATCH --qos=admin

mkdir -p {{node_name}}

# copy linpack
cd {{node_name}}

cat >> linpack_input << EOF
Sample Intel(R) Optimized LINPACK Benchmark data file (lininput_xeon64)
Intel(R) Optimized LINPACK Benchmark data
6                     # number of tests
1000 2000 5000 10000 20000 25000# problem sizes
1000 2000 5000 10000 20000 25000 # leading dimensions
2 2 2 1 1 1  # times to run a test
4 4 4 4 4 4  # alignment values (in KBytes)
EOF

# . /curc/tools/utils/dkinit
# use .openmpi-1.4.5_intel-12.1.2
# use Benchmarks

module load openmpi/openmpi-1.6.4_intel-13.0.0_torque-4.1.4_ib

echo "STREAM Memory Bandwidth Test:" > data
#----------------------------------------------------------------------------
export OMP_NUM_THREADS=12
NUM_TRIALS=2
COPYTOTAL=0
SCALETOTAL=0
ADDTOTAL=0
TRIADTOTAL=0
start_time=$(date +%s)
for ((i=0; i < NUM_TRIALS ; i++ ))
do
# Grab the 3 lines in addition to the line starting with Copy
VAR=`./lib/stream/stream-5.9/stream | grep -A 3 Copy`

COPY=`echo $VAR | awk '{ print $2 }' | awk -F. '{ print $1 }'`
COPYTOTAL=$(($COPY + $COPYTOTAL))

SCALE=`echo $VAR | awk '{ print $7 }' | awk -F. '{ print $1 }'`
SCALETOTAL=$(($SCALE + $SCALETOTAL))

ADD=`echo $VAR | awk '{ print $12 }' | awk -F. '{ print $1 }'`
ADDTOTAL=$(($ADD + $ADDTOTAL))

TRIAD=`echo $VAR | awk '{ print $17 }' | awk -F. '{ print $1 }'`
TRIADTOTAL=$(($TRIAD + $TRIADTOTAL))

done
end_time=$(date +%s)
echo $((end_time - start_time)) > time_data

echo $((COPYTOTAL/NUM_TRIALS)) " " $((SCALETOTAL/NUM_TRIALS)) " " $((ADDTOTAL/NUM_TRIALS)) " " $((TRIADTOTAL/NUM_TRIALS)) >> data

# Linpack
echo "Linpack CPU Test:" >> data
#----------------------------------------------------------------------------
start_time=$(date +%s)
./lib/linpack/linpack_11.2.2/benchmarks/linpack/xlinpack_xeon64 linpack_input | grep -A 9 Performance >> data
end_time=$(date +%s)
echo $((end_time - start_time)) >> time_data
"""

##CHANGES TO NODE_TEMPLATE
#Replace /home/molu8455/projects/redhat_6/software/linpack/linpack_11.0.3/benchmarks/linpack/xlinpack_xeon64 linpack_input | grep -A 9 Performance >> data
#With ./lib/linpack/linpack_11.2.2/benchmarks/linpack/xlinpack_xeon64 linpack_input | grep -A 9 Performance >> data
#Replace VAR=`/home/molu8455/projects/redhat_6/software/stream/stream | grep -A 3 Copy`
#With VAR=`./lib/stream/stream-5.9/stream | grep -A 3 Copy`

def create_pbs_template(values, mypath):
    output_file = os.path.join(mypath,"script_" + values['node_name'])
    #print output_file
    file_out = open(output_file,'w')
    t = Template(NODE_TEMPLATE)
    contents = t.render(**values)
    file_out.write(contents)
    file_out.close()

def create(node_list, queue, path):
    mypath = os.path.join(path,"nodes")
    util.create_directory_structure(mypath)

    # print mypath, node_list

    for node in node_list:

        # create the pbs command
        values = {}
        values['node_name'] = node
        values['queue_name'] = queue
        create_pbs_template(values, mypath)


#==============================================================================
if __name__ == '__main__':

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-q", "--queue", dest="queue", help="PBS Queue")
    parser.add_option("-l", "--list", dest="list", help="A list of nodes to run on")
    (options, args) = parser.parse_args()

    # default options
    queue = "janus-admin"
    node_list_name = None

    # get the options
    if options.queue != None:
        queue = options.queue
    if options.list != None:
        node_list_name = options.list
        node_list = read_node_list(node_list_name)
        #print node_list
    else:
        print "please specify a node list."
        exit()

    print "creating Node tests"

    current_path = os.getcwd()
    create(node_list, queue, current_path)
