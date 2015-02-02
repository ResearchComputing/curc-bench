#!/curc/admin/benchmarks/bin/python
import fileinput, os, sys
import math
import numpy
from scipy import stats

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
        return time_est*factor_est

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

def create_pbs_file(N,P,Q,job_name, time_est):
    source_path = sys.path[0]
    current_path = os.getcwd()
    template_file = os.path.join(source_path,"template_HPL")
    output_file = os.path.join(current_path,"script_" + job_name)
    nodes = P*Q/12
    processors = P*Q

    file_in = open(template_file);
    file_out = open(output_file,'w');

    for line in file_in:
        tmp = line.replace('<JOB_NAME>',job_name)
        estt = math.floor(time_est*10)
        estt = min(estt, 6*60*60)

        tmp = tmp.replace('<TIME>', str(estt))
        tmp = tmp.replace('<NODES>', str(nodes))
        tmp = tmp.replace('<PROCESSORS>', str(processors))
        tmp = tmp.replace('<N>', str(N))
        tmp = tmp.replace('<P>', str(P))
        tmp = tmp.replace('<Q>', str(Q))
        file_out.write(tmp)
    file_in.close()
    file_out.close()

#==============================================================================
# how many nodes?
nodes = int(sys.argv[1])

percent = 20
if( len(sys.argv) > 2 ):
    percent = int(sys.argv[2])

# What's the best P and Q
PQ = closest_match(nodes*processors_per_node())

time_model = TimeModel()
time_estimate = time_model.get_time_estimate(nodes, percent)

# Max problem size?
N = max_matrix_dimension(nodes,(float(percent)/100))

job_name = "hpl-" + str(nodes) + "-" + str(percent)

create_pbs_file(N,PQ[0],PQ[1],job_name, time_estimate)
