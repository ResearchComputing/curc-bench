import bench.tests.alltoall
import bench.tests.bandwidth
import bench.tests.node
import bench.util
from bench.util import util as util
import datetime
import logging
import os
import subprocess


logger = logging.getLogger('Benchmarks')

import util.util
import create_tests.create_node_test as create_node_test
import create_tests.create_bandwidth_test as create_bandwidth_test
import create_tests.create_alltoall2 as create_alltoall
#import create_tests.create_hpl_test as create_hpl
#import create_tests.create_scaling as create_scaling

from bench.util import util as util

def execute(prefix, topology_file, alltoall_rack, alltoall_switch,
            alltoall_pair, bandwidth, nodes):
    node_list = util.read_node_list(os.path.join(prefix, 'node_list'))
    logger.info('nodes: {0}'.format(len(node_list)))

    if topology_file is not None:
        topology = bench.util.infiniband.get_topology(topology_file)
    else:
        topology = {}

    if not (alltoall_rack or alltoall_switch or alltoall_pair or bandwidth or nodes):
        add_node_tests(node_list, prefix)
        add_bandwidth_tests(node_list, topology, prefix)
        add_alltoall_rack_tests(node_list, prefix)
        add_alltoall_switch_tests(node_list, topology, prefix)
        add_alltoall_pair_tests(node_list, topology, prefix)

    else:
        if alltoall_rack:
            add_alltoall_rack_tests(node_list, prefix)
        if alltoall_switch:
            add_alltoall_switch_tests(node_list, topology, prefix)
        if alltoall_pair:
            add_alltoall_pair_tests(node_list, topology, prefix)
        if bandwidth:
            add_bandwidth_tests(node_list, topology, prefix)
        if nodes:
            add_node_tests(node_list, prefix)


def add_node_tests (node_list, prefix):
    node_prefix = os.path.join(prefix, 'node')
    logger.info('adding node tests to {0}'.format(node_prefix))
    bench.util.mkdir_p(node_prefix)
    bench.tests.node.generate(node_list, node_prefix)


def add_bandwidth_tests (node_list, topology, prefix):
    bandwidth_prefix = os.path.join(prefix, 'bandwidth')
    logger.info('adding bandwidth tests to {0}'.format(bandwidth_prefix))
    bench.util.mkdir_p(bandwidth_prefix)
    bench.tests.bandwidth.generate(node_list, topology, bandwidth_prefix)


def add_alltoall_rack_tests (node_list, prefix):
    alltoall_rack_prefix = os.path.join(prefix, 'alltoall-rack')
    logger.info('adding alltoall-rack tests to {0}'.format(alltoall_rack_prefix))
    bench.util.mkdir_p(alltoall_rack_prefix)
    bench.tests.alltoall.generate_alltoall_rack(node_list, alltoall_rack_prefix)


def add_alltoall_switch_tests (node_list, topology, prefix):
    alltoall_switch_prefix = os.path.join(prefix, 'alltoall-switch')
    logger.info('adding alltoall-switch tests to {0}'.format(alltoall_switch_prefix))
    bench.util.mkdir_p(alltoall_switch_prefix)
    bench.tests.alltoall.generate_alltoall_switch(node_list, topology, alltoall_switch_prefix)


def add_alltoall_pair_tests (node_list, topology, prefix):
    alltoall_pair_prefix = os.path.join(prefix, 'alltoall-pair')
    logger.info('adding alltoall-pair tests to {0}'.format(alltoall_pair_prefix))
    bench.util.mkdir_p(alltoall_pair_prefix)
    bench.tests.alltoall.generate_alltoall_pair(node_list, topology, alltoall_pair_prefix)
