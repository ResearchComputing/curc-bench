import bench.tests.alltoall
import bench.tests.bandwidth
import bench.tests.node
import bench.util
import logging
import os


logger = logging.getLogger(__name__)


GENERATORS = {
    'node': bench.tests.node.generate,
    'bandwidth': bench.tests.bandwidth.generate,
    'alltoall-rack': bench.tests.alltoall.generate_alltoall_rack,
    'alltoall-switch': bench.tests.alltoall.generate_alltoall_switch,
    'alltoall-pair': bench.tests.alltoall.generate_alltoall_pair,
}


def execute(prefix, topology_file,
            alltoall_rack_tests=None,
            alltoall_switch_tests=None,
            alltoall_pair_tests=None,
            bandwidth_tests=None,
            node_tests=None):
    node_list = bench.util.read_node_list(os.path.join(prefix, 'node_list'))

    if topology_file is not None:
        topology = bench.util.infiniband.get_topology(topology_file)
    else:
        topology = {}

    add_any_tests_explicitly = (
        alltoall_rack_tests
        or alltoall_switch_tests
        or alltoall_pair_tests
        or bandwidth_tests
        or node_tests)

    # default to adding *all* tests
    if not add_any_tests_explicitly:
        for key in PROCESSORS:
            add_tests(node_list, prefix, key, topology)
    else:
        if alltoall_rack_tests:
            add_tests(node_list, prefix, 'alltoall-rack', topology)
        if alltoall_switch_tests:
            add_tests(node_list, prefix, 'alltoall-switch', topology)
        if alltoall_pair_tests:
            add_tests(node_list, prefix, 'alltoall-pair', topology)
        if bandwidth_tests:
            add_tests(node_list, prefix, 'bandwidth', topology)
        if node_tests:
            add_tests(node_list, prefix, 'node', topology)


def add_tests (node_list, prefix, key, topology=None):
    tests_prefix = os.path.join(prefix, key, 'tests')
    logger.info('adding {0} tests to {1}'.format(key, tests_prefix))
    bench.util.mkdir_p(tests_prefix)
    if key in ('bandwidth', 'alltoall-switch', 'alltoall-pair'):
        GENERATORS[key](node_list, topology, tests_prefix)
    else:
        GENERATORS[key](node_list, tests_prefix)
