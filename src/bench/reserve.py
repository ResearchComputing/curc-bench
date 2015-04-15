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

    # :param int flags: Slurm reservation flags
    #     - RESERVE_FLAG_MAINT              0x0001
    #     - RESERVE_FLAG_NO_MAINT           0x0002
    #     - RESERVE_FLAG_DAILY              0x0004
    #     - RESERVE_FLAG_NO_DAILY           0x0008
    #     - RESERVE_FLAG_WEEKLY             0x0010
    #     - RESERVE_FLAG_NO_WEEKLY          0x0020
    #     - RESERVE_FLAG_IGN_JOBS           0x0040
    #     - RESERVE_FLAG_NO_IGN_JOB         0x0080
    #     - RESERVE_FLAG_LIC_ONLY           0x0100
    #     - RESERVE_FLAG_NO_LIC_ONLY        0x0200
    #     - RESERVE_FLAG_OVERLAP            0x4000
    #     - RESERVE_FLAG_SPEC_NODES         0x8000

    # create_reservation_dict() returns empty dict with:
    # return {u'start_time': -1,
    #         u'end_time': -1,
    #         u'duration': -1,
    #         u'node_cnt': -1,
    #         u'name': '',
    #         u'node_list': '',
    #         u'flags': '',
    #         u'partition': '',
    #         u'licenses': '',
    #         u'users': '',
    #         u'accounts': ''}

            a = pyslurm.reservation()
            res_dict = pyslurm.create_reservation_dict()
            res_dict['accounts'] = 'crcbenchmark'
            res_dict['flags'] = 16384  #flag for 'OVERLAP'
            res_dict['start_time'] = calendar.timegm(time.gmtime()) #time right now
            res_dict['duration'] = 2678400                    #32 days
            res_dict['name'] = label
            res_dict['node_list'] = node_string[:-1]          #Check formatting!
            #Note sure if 'nodes' or 'node_list' should be used. Documentation is bad...
            #res_dict['nodes'] = node_string[:-1]    

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
