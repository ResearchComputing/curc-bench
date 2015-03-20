#!/usr/bin/env python

import os
import subprocess
import datetime
import shutil
import textwrap
import re
import datetime

from util.hostlist import expand_hostlist
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

    pid = subprocess.Popen('scontrol show reservation', shell=True,
                           stdout=subprocess.PIPE)
    pid.wait()
    output, error = pid.communicate()
    tmp = re.findall(r'ReservationName=([0-9]+.[0-9]+PM-janus) StartTime=([0-9]+-[0-9]+-[0-9]+)', output)
    print tmp

    import time

    # is there more than one?
    queue_name = tmp[0][0]
    queue_time = datetime.datetime.strptime(tmp[0][1], "%Y-%m-%d")

    # queue_date = date.fromtimestamp(tmp[0][1])
    print queue_time
    if len(tmp) > 1:
      # find the min...
        for i in tmp[1:]:
            i_name = i[0]
            i_time = i[1]
            i_var = datetime.datetime.strptime(i_time, "%Y-%m-%d")
            if (i_var - queue_time).days < 0:
                queue_name = i_name
                queue_time = i_var

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
