import os
import subprocess
import datetime
import shutil
import textwrap
import re
import datetime
import pyslurm

from util.xml2obj import xml2obj

import logging
logger = logging.getLogger('Benchmarks')

import util.util
import create_tests.create_node_test as create_node_test
import create_tests.create_bandwidth_test as create_bandwidth_test
import create_tests.create_alltoall2 as create_alltoall
#import create_tests.create_hpl_test as create_hpl
#import create_tests.create_scaling as create_scaling

from bench.util import util as util



def execute(directory, args):

    logger.info(directory)
    print directory
    queue_name = 'janus-admin'

    a = pyslurm.reservation()
    reserve_dict = a.get()
    queue_name = ''
    queue_time = ''

    for key, value in reserve_dict.iteritems():
        if key.endswith('PM-janus'):
            queue_name = key
            for part_key in sorted(value.iterkeys()):
                if part_key == "start_time":
                    time1 = datetime.datetime.fromtimestamp(int(value[part_key]))
                    time1 = time1.replace(hour=0, minute=0, second=0, microsecond=0)
                    queue_time = time1

    # queue_date = date.fromtimestamp(tmp[0][1])
    print queue_time

    logger.info("Using the PM-janus queue with the oldest time stamp.")
    logger.info("queue name".ljust(20)+queue_name.rjust(5))
    node_list = util.read_node_list(os.path.join(directory,'node_list'))
    logger.info("Node list".ljust(20)+str(len(node_list)).rjust(5))

    if not args.allrack and not args.allswitch and not args.bandwidth and not args.nodes and not args.allpair:

        #Create the tests
        logger.info("node tests")
        create_node_test.create(node_list,queue_name,directory)

        logger.info("bandwidth tests")
        create_bandwidth_test.create(node_list,queue_name,directory)

        logger.info("alltoall tests")
        create_alltoall.create(node_list,queue_name,directory)

        create_scaling.create(node_list,"janus-admin",directory)

    else:

        if args.allrack or args.allswitch or args.allpair:
           logger.info("alltoall tests")
           create_alltoall.create(node_list,queue_name,directory, args)

        if args.bandwidth:
           logger.info("bandwidth tests")
           create_bandwidth_test.create(node_list,queue_name,directory)

        if args.nodes:
           logger.info("node tests")
           create_node_test.create(node_list,queue_name,directory)
