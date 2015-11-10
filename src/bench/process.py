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
            process_tests(prefix, key)
    else:
        if alltoall_rack_tests:
            process_tests(prefix, 'alltoall-rack')
        if alltoall_switch_tests:
            process_tests(prefix, 'alltoall-switch')
        if alltoall_pair_tests:
            process_tests(prefix, 'alltoall-pair')
        if bandwidth_tests:
            process_tests(prefix, 'bandwidth')
        if node_tests:
            process_tests(prefix, 'node')


def process_tests (prefix, key):
    prefix_ = os.path.join(prefix, key, 'tests')
    if not os.path.exists(prefix_):
        logger.warn('{0}: not found'.format(key))
        return
    node_list = bench.util.read_node_list(os.path.join(prefix, key, 'node_list'))
    results = PROCESSORS[key](node_list, prefix_)
    logger.info('{0}: fail nodes: {1} / {2}'.format(
        key, len(results['fail_nodes']), len(node_list)))
    logger.info('{0}: pass nodes: {1} / {2}'.format(
        key, len(results['pass_nodes']), len(node_list)))
    logger.info('{0}: error nodes: {1} / {2}'.format(
        key, len(results['error_nodes']), len(node_list)))
    write_result_files(
        os.path.join(prefix, key),
        results['pass_nodes'],
        results['fail_nodes'],
        results['error_nodes'],
    )


def write_result_files(prefix, pass_nodes, fail_nodes, error_nodes):
    bench.util.write_node_list(
        os.path.join(prefix, 'pass_nodes'),
        pass_nodes,
    )

    bench.util.write_node_list(
        os.path.join(prefix, 'fail_nodes'),
        fail_nodes,
    )

    bench.util.write_node_list(
        os.path.join(prefix, 'error_nodes'),
        error_nodes,
    )
