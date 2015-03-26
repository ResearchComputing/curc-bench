from jinja2 import Template

import fileinput, os, sys
import math
import numpy
from scipy import stats
import uuid

from bench.util import util
from bench.util import infiniband
from bench.util import config

import logging
logger = logging.getLogger('Benchmarks')

HPL_TEMPLATE = """\
#!/bin/bash
#PBS -N job.{{id}}
#PBS -q {{queue}}
#PBS -l walltime={{time_estimate}}
#PBS -l nodes={% for x in node_list %}{{x}}:ppn=12{% if not loop.last %}+{%endif%}{% endfor %}
#PBS -j oe

cd $PBS_O_WORKDIR

module load openmpi/openmpi-1.6.4_intel-13.0.0_torque-4.1.4_ib

mkdir -p test_{{id}}
cd test_{{id}}

cat >> linpack_input << EOF
Sample Intel(R) Optimized LINPACK Benchmark data file (lininput_xeon64)
Intel(R) Optimized LINPACK Benchmark data
6                     # number of tests
1000 2000 5000 10000 20000 25000# problem sizes
1000 2000 5000 10000 20000 25000 # leading dimensions
2 2 2 1 1 1  # times to run a test
4 4 4 4 4 4  # alignment values (in KBytes)
EOF

./lib/linpack/linpack_11.2.2/benchmarks/linpack/xlinpack_xeon64 linpack_input | grep -A 9 Performance >> data

"""
##CHANGES TO HPL_TEMPLATE
#Replace /home/molu8455/projects/redhat_6/software/linpack/linpack_11.0.3/benchmarks/linpack/xlinpack_xeon64 linpack_input | grep -A 9 Performance >> data
#With ./lib/linpack/linpack_11.2.2/benchmarks/linpack/xlinpack_xeon64 linpack_input | grep -A 9 Performance >> data

# These are parameters for the script
#==============================================================================
def processors_per_node():
    return 12

def memory_per_node():
     return 20*1073741824

# The class for modeling time
#==============================================================================
class TimeModel:
    def __init__(self):
        # fixed at 20%: processors vs. time
        x1 = [ 12,  24,  48,  96, 192, 384, 768, ]
        y1 = [72.61, 104.29, 150.38, 215.10, 314.19, 455.94, 681.95]
        self.g1, self.i1, r, p, std_err = stats.linregress( numpy.log(x1), numpy.log(y1))

        # fixed at 8 nodes: percent vs. time
        x2 = [ 20, 40, 60, 80 ]
        y2 = [ 215.10, 583.83, 1056.89, 1617.62]
        y2 = numpy.divide(y2,215.10)
        self.g2, self.i2, r, p, std_err = stats.linregress( numpy.log(x2), numpy.log(y2))

    def get_time_estimate(self, nodes, percent):
        tmp = self.g1 * numpy.log(nodes*12) + self.i1
        time_est = numpy.exp(tmp)

        tmp = self.g2 * numpy.log(percent) + self.i2
        factor_est = numpy.exp(tmp)
        return round(time_est*factor_est)*10

def max_matrix_dimension(nodes, percent):
    tmp = memory_per_node()*nodes*percent/8
    return int(math.floor(math.sqrt(tmp)))

def factor(n):
    if n == 1: return [1]
    i = 2
    limit = n**0.5
    while i <= limit:
        if n % i == 0:
            ret = factor(n/i)
            ret.append(i)
            return ret
        i += 1
    return [n]

def closest_match(n):
    factors = factor(n)
    index = 1
    A = numpy.multiply.reduce(factors[:index])
    B = numpy.multiply.reduce(factors[index:])
    diff = abs(A-B)
    while index < len(factors):
        tmpA = numpy.multiply.reduce(factors[:index])
        tmpB = numpy.multiply.reduce(factors[index:])
        if( abs(tmpA-tmpB) < diff):
            diff = abs(tmpA-tmpB)
            A = tmpA
            B = tmpB
        index += 1
    values = [A,B]
    values.sort()
    return values

def create_pbs_template(mypath, hpl):
    logger.debug("HPL test "+hpl['id'] + " " + str(hpl['nodes']))
    output_file = os.path.join(mypath,"script_" + hpl['job_name'] + "-" + hpl['id'])
    file_out = open(output_file,'w')
    t = Template(HPL_TEMPLATE)
    contents = t.render(**hpl)
    file_out.write(contents)
    file_out.close()

def create_node_groups(node_list,n):
    total_nodes = len(node_list)
    x = math.floor(total_nodes/float(n))
    y = math.ceil(total_nodes/float(n))

    node_groups = []

    #print "create " + str(x) + " groups with " + str(n) + " nodes"
    index = 0
    for r in range(int(x)):
        tmp = []
        for i in range(int(n)):
            tmp.append(node_list[index].rstrip())
            index += 1
        #print tmp
        node_groups.append(tmp)

    #print "create 1 group with " + str(total_nodes - x*n) + " nodes"
    if total_nodes - x*n > 0:
        tmp = []
        for i in range(int(total_nodes - x*n)):
            tmp.append(node_list[i].rstrip())
        #print tmp
        node_groups.append(tmp)

    #print node_groups
    return node_groups

def render(mypath, queue, node_list):
    #percent = 80
    percent = config.hpl_percent
    n = len(node_list)
    #print n
    hpl = {}

    hpl['queue'] = queue
    # What's the best P and Q
    PQ = closest_match(n*processors_per_node())
    hpl['p'] = PQ[0]
    hpl['q'] = PQ[1]
    hpl['id'] = str(uuid.uuid1())
    #hpl['id'] = str(111)
    hpl['nodes'] = n
    hpl['processors'] = n*processors_per_node()
    hpl['node_list'] = node_list
    hpl['percent'] = percent

    time_model = TimeModel()
    time_estimate = time_model.get_time_estimate(n, percent)
    #print time_estimate
    hpl['time_estimate'] = time_estimate

    # Max problem size?
    N = max_matrix_dimension(n,(float(percent)/100))
    hpl['n'] = N

    job_name = "hpl-" + str(n) + "-" + str(percent)

    hpl['job_name'] = job_name

    create_pbs_template(mypath, hpl)


def create(node_list, queue, path):
    #print node_list
    mypath = os.path.join(path,"hpl")
    util.create_directory_structure(mypath)

    logger.info("HPL with pecent = "+str(config.hpl_percent))
    # Test with 18 nodes on a switch
    logger.info("Creating 18 node HPL tests")
    rack_switch = infiniband.rack_switch_18(node_list)
    rack_list = []
    for name, name_list in rack_switch.iteritems():
        #print name, name_list
        if len(name_list) > 0:
             render(mypath, queue, name_list)
             rack_list.extend(name_list)
             data = infiniband.rack_list_subsets(name_list)
             for j,k in data.iteritems():
                 render(mypath, queue, k)

    logger.debug("not tested "+ str(len(set(node_list).difference(set(rack_list)))))



    # Test with 18 nodes on a switch
    # logger.info("Creating 18 node alltoall tests")
    #     rack_switch = rack_switch_18(node_list)
    #     rack_list = []
    #     for name, name_list in rack_switch.iteritems():
    #         #print name, name_list
    #         if len(name_list) > 0:
    #              render(mypath, queue, name_list)
    #              rack_list.extend(name_list)
    #
    #     logger.debug("not tested"+ str(set(node_list).difference(set(rack_list))))




# def create(name_list, queue, n, percent, dir_name):
#     current_path = os.getcwd()
#     mypath = os.path.join(current_path, dir_name)
#     create_directory_structure(mypath)
#
#     groups = create_node_groups(name_list,n)
#     for i in range(len(groups)):
#         render(mypath, queue, groups[i], percent)
