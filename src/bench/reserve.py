import os
import subprocess
from bench.util import util
import pyslurm
import time
import calendar

import logging
logger = logging.getLogger('Benchmarks')

def create_reservation(data_name, label, directory):

    data = util.read_node_list(data_name, directory)

    #print data
    try:
        if len(data) > 0:
            logger.info(label)
            # Adding ^ to fix cnode01.. node01.. issue
            #node_string = "".join(['^%s$,' % n for n in data])
            node_string = "".join(['%s,' % n for n in data])

            # print node_string[:-1]
            # os.environ['NODE_LIST'] = node_string[:-1]
            # cmd = 'scontrol create reservation={0} accounts=crcbenchmark flags=overlap starttime=now duration=32-0 nodes=$NODE_LIST'.format(label)
            
            # print cmd
            # cmd_out = subprocess.check_output([cmd] , shell=True)
            a = pyslurm.reservation()
            res_dict = pyslurm.create_reservation_dict()
            res_dict['accounts'] = 'crcbenchmark'            #Is this the desired account name?
            res_dict['flags'] = 'overlap'
            res_dict['start_time'] = calendar.timegm(time.gmtime()) #time right now
            res_dict['duration'] = 2678400                    #32 days
            res_dict['name'] = label
            res_dict['node_list'] = node_string[:-1]          #Check formatting!

            resid = a.create(res_dict)

            if pyslurm.slurm_get_errno() != 0:
                print "Failed - Error : %s" % pyslurm.slurm_strerror(pyslurm.slurm_get_errno())
            else:
                print "Success - Created reservation %s\n" % resid
                res_display(a.get())


    except:
        logger.error("could not create " + label + " reservations")



def execute(directory, allrack=None, allswitch=None,
            bandwidth=None, nodes=None, allpair=None):

    logger.info(directory)

    if not (allrack or allswitch or bandwidth or nodes or allpair):
    # if not args.allrack and not args.allswitch and not args.bandwidth and not args.nodes and not args.allpair:

         create_reservation( "list_all_rack_bad_not_tested_nodes", "benchmark-alltoall-rack", directory)
         create_reservation( "list_all_switch_bad_not_tested_nodes", "benchmark-alltoall-switch", directory)
         create_reservation( "list_all_pair_bad_not_tested_nodes", "benchmark-alltoall-pair", directory)
         create_reservation( "list_band_bad_not_tested_nodes", "benchmark-bandwidth", directory)
         create_reservation( "list_node_bad_not_tested_nodes", "benchmark-node", directory)
         # create_reservation( "not_tested", "benchmark-not-tested",directory)
         create_reservation( "not_in_test", "benchmark-not-in-test", directory)

    else:

        print args

        if allrack==True:
           create_reservation( "list_all_rack_bad_not_tested_nodes", "benchmark_alltoall_rack", directory)

        if allswitch==True:
           create_reservation( "list_all_switch_bad_not_tested_nodes", "benchmark_alltoall_switch", directory)

        if allpair==True:
           create_reservation( "list_all_pair_bad_not_tested_nodes", "benchmark_alltoall_pair", directory)

        if bandwidth==True:
            create_reservation( "list_band", "benchmark_bandwidth", directory)

        if nodes==True:
            create_reservation( "list_node", "benchmark_node", directory)
            #create_reservation( "not_tested", "benchmark-not-tested",directory)
            #create_reservation( "not_in_test", "benchmark-not-in-test",directory)


    print ""
