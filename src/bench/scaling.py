import bench.tests.scaling
import bench.tests.hpl
from bench.util import util
from bench.util import infiniband
from bench.util import config
import fileinput
import logging
import math
import os
import sys
import uuid


logger = logging.getLogger('Benchmarks')


def execute(directory):
    logger.info(directory)

    node_list = util.read_node_list(os.path.join(directory,'node_list'))
    logger.info("Node list".ljust(20)+str(len(node_list)).rjust(5))

    mypath = os.path.join(directory,"scaling")
    util.create_directory_structure(mypath)

    logger.info("Creating Scaling Tests")
    rack_switch = infiniband.get_switch_nodes(node_list)
    preference_list = []
    for name, name_list in rack_switch.iteritems():
        if len(name_list) > 0:
             for n in name_list:
                 preference_list.append(n)

    num_nodes =  len(set(preference_list))
    logger.info("Number of nodes available for test "+str(num_nodes))

    i = 1
    while i < num_nodes:
        logger.info("creating test "+str(i))

        bench.test.hpl.render(mypath,'janus-admin',preference_list[:i])
        bench.tests.scaling.render(mypath,preference_list[:i])

        i *= 2
