import os
import subprocess
from bench.util import util

import logging
logger = logging.getLogger('Benchmarks')

def create_reservation(data_name,label,directory):

    data = util.read_node_list(data_name,directory)

    #print data
    try:
        if len(data) > 0:
            logger.info(label)
            # Adding ^ to fix cnode01.. node01.. issue
            #node_string = "".join(['^%s$,' % n for n in data])
            node_string = "".join(['%s,' % n for n in data])
            print node_string[:-1]
            os.environ['NODE_LIST'] = node_string[:-1]
            #cmd = "mrsvctl -c -h $NODE_LIST -n " + label
            cmd = 'scontrol create reservation={0} accounts=crcbenchmark flags=overlap starttime=now duration=32-0 nodes=$NODE_LIST'.format(label)

            print cmd
            cmd_out = subprocess.check_output([cmd] , shell=True)
    except:
        logger.error("could not create " + label + " reservations")

    # Remove cnodes


        #print cmd_out

def release_reservations(data):

    for d in data:
        if d != 'benchmark-not-tested.30472' and d != 'benchmark-nodes.30471':
            logger.info(d)
            cmd = "mrsvctl -r " + d
            cmd_out = subprocess.check_output([cmd] , shell=True)
            #print cmd_out


def execute(directory, args):

    logger.info(directory)


    if not args.allrack and not args.allswitch and not args.bandwidth and not args.nodes and not args.allpair:

         create_reservation( "list_all_rack_bad_not_tested_nodes", "benchmark-alltoall-rack",directory)
         create_reservation( "list_all_switch_bad_not_tested_nodes", "benchmark-alltoall-switch",directory)
         create_reservation( "list_all_pair_bad_not_tested_nodes", "benchmark-alltoall-pair",directory)
         create_reservation( "list_band_bad_not_tested_nodes", "benchmark-bandwidth",directory)
         create_reservation( "list_node_bad_not_tested_nodes", "benchmark-node",directory)
         # create_reservation( "not_tested", "benchmark-not-tested",directory)
         create_reservation( "not_in_test", "benchmark-not-in-test",directory)

    else:

        print args

        if args.allrack==True:
           create_reservation( "list_all_rack_bad_not_tested_nodes", "benchmark_alltoall_rack",directory)

        if args.allswitch==True:
           create_reservation( "list_all_switch_bad_not_tested_nodes", "benchmark_alltoall_switch",directory)

        if args.allpair==True:
           create_reservation( "list_all_pair_bad_not_tested_nodes", "benchmark_alltoall_pair",directory)

        if args.bandwidth==True:
            create_reservation( "list_band", "benchmark_bandwidth",directory)

        if args.nodes==True:
            create_reservation( "list_node", "benchmark_node",directory)
            #create_reservation( "not_tested", "benchmark-not-tested",directory)
            #create_reservation( "not_in_test", "benchmark-not-in-test",directory)


    print ""
