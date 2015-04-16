import bench.tests.alltoall
import bench.tests.bandwidth
import bench.tests.node
import bench.util
import logging
import os


logger = logging.getLogger('Benchmarks')


def execute(prefix, topology_file,
            add_alltoall_rack_tests=None,
            add_alltoall_switch_tests=None,
            add_alltoall_pair_tests=None,
            add_bandwidth_tests=None,
            add_node_tests=None):
    node_list = bench.util.read_node_list(os.path.join(prefix, 'node_list'))
    logger.info('nodes: {0}'.format(len(node_list)))

    if topology_file is not None:
        topology = bench.util.infiniband.get_topology(topology_file)
    else:
        topology = {}

    add_any_tests_explicitly = (
        add_alltoall_rack_tests
        or add_alltoall_switch_tests
        or add_alltoall_pair_tests
        or add_bandwidth_tests
        or add_node_tests)

    # default to adding *all* tests
    if not add_any_tests_explicitly:
        _add_node_tests(node_list, prefix)
        _add_bandwidth_tests(node_list, topology, prefix)
        _add_alltoall_rack_tests(node_list, prefix)
        _add_alltoall_switch_tests(node_list, topology, prefix)
        _add_alltoall_pair_tests(node_list, topology, prefix)

    else:
        if add_alltoall_rack_tests:
            _add_alltoall_rack_tests(node_list, prefix)
        if add_alltoall_switch_tests:
            _add_alltoall_switch_tests(node_list, topology, prefix)
        if add_alltoall_pair_tests:
            _add_alltoall_pair_tests(node_list, topology, prefix)
        if add_bandwidth_tests:
            _add_bandwidth_tests(node_list, topology, prefix)
        if add_node_tests:
            _add_node_tests(node_list, prefix)


def _add_node_tests (node_list, prefix):
    node_prefix = os.path.join(prefix, 'node')
    logger.info('adding node tests to {0}'.format(node_prefix))
    bench.util.mkdir_p(node_prefix)
    bench.tests.node.generate(node_list, node_prefix)


def _add_bandwidth_tests (node_list, topology, prefix):
    bandwidth_prefix = os.path.join(prefix, 'bandwidth')
    logger.info('adding bandwidth tests to {0}'.format(bandwidth_prefix))
    bench.util.mkdir_p(bandwidth_prefix)
    bench.tests.bandwidth.generate(node_list, topology, bandwidth_prefix)


def _add_alltoall_rack_tests (node_list, prefix):
    alltoall_rack_prefix = os.path.join(prefix, 'alltoall-rack')
    logger.info('adding alltoall-rack tests to {0}'.format(alltoall_rack_prefix))
    bench.util.mkdir_p(alltoall_rack_prefix)
    bench.tests.alltoall.generate_alltoall_rack(node_list, alltoall_rack_prefix)


def _add_alltoall_switch_tests (node_list, topology, prefix):
    alltoall_switch_prefix = os.path.join(prefix, 'alltoall-switch')
    logger.info('adding alltoall-switch tests to {0}'.format(alltoall_switch_prefix))
    bench.util.mkdir_p(alltoall_switch_prefix)
    bench.tests.alltoall.generate_alltoall_switch(node_list, topology, alltoall_switch_prefix)


def _add_alltoall_pair_tests (node_list, topology, prefix):
    alltoall_pair_prefix = os.path.join(prefix, 'alltoall-pair')
    logger.info('adding alltoall-pair tests to {0}'.format(alltoall_pair_prefix))
    bench.util.mkdir_p(alltoall_pair_prefix)
    bench.tests.alltoall.generate_alltoall_pair(node_list, topology, alltoall_pair_prefix)
