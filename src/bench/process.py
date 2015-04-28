import bench.util
import bench.tests.node
import bench.tests.bandwidth
import bench.tests.alltoall
import hostlist
import logging
import os


logger = logging.getLogger(__name__)


PROCESSORS = {
    'node': bench.tests.node.process,
    'bandwidth': bench.tests.bandwidth.process,
    'alltoall-rack': bench.tests.alltoall.process,
    'alltoall-switch': bench.tests.alltoall.process,
    'alltoall-pair': bench.tests.alltoall.process,
}


def execute(prefix,
            alltoall_rack_tests=None,
            alltoall_switch_tests=None,
            alltoall_pair_tests=None,
            bandwidth_tests=None,
            node_tests=None):
    node_list = bench.util.read_node_list(os.path.join(prefix, 'node_list'))

    process_any_tests_explicitly = (
        alltoall_rack_tests
        or alltoall_switch_tests
        or alltoall_pair_tests
        or bandwidth_tests
        or node_tests
    )

    # default to processing *all* test results
    if not process_any_tests_explicitly:
        for key in PROCESSORS:
            process_tests(node_list, prefix, key)
    else:
        if alltoall_rack_tests:
            process_tests(node_list, prefix, 'alltoall-rack')
        if alltoall_switch_tests:
            process_tests(node_list, prefix, 'alltoall-switch')
        if alltoall_pair_tests:
            process_tests(node_list, prefix, 'alltoall-pair')
        if bandwidth_tests:
            process_tests(node_list, prefix, 'bandwidth')
        if node_tests:
            process_tests(node_list, prefix, 'node')


def process_tests (node_list, prefix, key):
    prefix_ = os.path.join(prefix, key, 'tests')
    results = PROCESSORS[key](node_list, prefix_)
    logger.info('{0}: bad nodes: {1} / {2}'.format(
        key, len(results['bad_nodes']), len(node_list)))
    logger.info('{0}: good nodes: {1} / {2}'.format(
        key, len(results['good_nodes']), len(node_list)))
    logger.info('{0}: untested nodes: {1} / {2}'.format(
        key, len(results['not_tested']), len(node_list)))
    write_result_files(
        os.path.join(prefix, key),
        results['good_nodes'],
        results['bad_nodes'],
        results['not_tested'],
    )
    return results


def write_result_files(prefix, good_nodes, bad_nodes, not_tested):
    bench.util.write_node_list(
        os.path.join(prefix, 'good_nodes'),
        good_nodes,
    )

    bench.util.write_node_list(
        os.path.join(prefix, 'bad_nodes'),
        bad_nodes,
    )

    bench.util.write_node_list(
        os.path.join(prefix, 'not_tested'),
        not_tested,
    )
