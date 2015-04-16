import bench.util
import bench.tests.node
import bench.import_tests.import_bandwidth
import bench.import_tests.import_alltoall
import hostlist
import logging
import os


logger = logging.getLogger('Benchmarks')


PROCESSORS = {
    'node': bench.tests.node.process,
    'bandwidth': bench.import_tests.import_bandwidth.execute,
    'alltoall-rack': bench.import_tests.import_alltoall.execute_rack,
    'alltoall-switch': bench.import_tests.import_alltoall.execute_switch,
    'alltoall-pair': bench.import_tests.import_alltoall.execute_pair,
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


def process_tests (nodes, prefix, key):
    prefix_ = os.path.join(prefix, key)
    results = PROCESSORS[key](nodes, prefix_)
    logger.info('{0}: bad nodes: {1} / {2}'.format(
        key, len(results['bad_nodes']), len(nodes)))
    logger.info('{0}: good nodes: {1} / {2}'.format(
        key, len(results['good_nodes']), len(nodes)))
    logger.info('{0}: untested nodes: {1} / {2}'.format(
        key, len(results['not_tested']), len(nodes)))
    write_result_files(
        prefix_,
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
