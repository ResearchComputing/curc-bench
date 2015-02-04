#!/curc/admin/benchmarks/bin/python
from django.conf import settings
from django import template
if not settings.configured:
    settings.configure()

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

from bench.create_tests import create_hpl_test as create_hpl_test
from bench.scaling_tests import python_test as python_test

def execute(directory):

    logger.info(directory)

    node_list = util.read_node_list(os.path.join(directory,'node_list'))
    logger.info("Node list".ljust(20)+str(len(node_list)).rjust(5))

    #print node_list
    mypath = os.path.join(directory,"scaling")
    util.create_directory_structure(mypath)

    logger.info("Creating Scaling Tests")
    rack_switch = infiniband.rack_switch_18(node_list)
    preference_list = []
    for name, name_list in rack_switch.iteritems():
        #print name, name_list
        if len(name_list) > 0:
             for n in name_list:
                 preference_list.append(n)

    num_nodes =  len(set(preference_list))
    logger.info("Number of nodes available for test "+str(num_nodes))

    i = 1
    while i < num_nodes:
        logger.info("creating test "+str(i))

        create_hpl_test.render(mypath,'janus-admin',preference_list[:i])
        python_test.render(mypath,preference_list[:i])

        i *= 2
