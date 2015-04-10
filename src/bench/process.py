import bench.util
import bench.util.util
import bench.import_tests.import_nodes
import bench.import_tests.import_bandwidth
import bench.import_tests.import_alltoall
import hostlist
import logging
import os


logger = logging.getLogger('Benchmarks')


PROCESSORS = {
    'node': bench.import_tests.import_nodes.execute,
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
    node_list = bench.util.util.read_node_list(os.path.join(prefix, 'node_list'))

    process_any_tests_explicitly = (
        alltoall_rack_tests
        or alltoall_switch_tests
        or alltoall_pair_tests
        or bandwidth_tests
        or node_tests
    )

    not_tested = set()
    bad_nodes = set()

    # default to processing *all* test results
    if not process_any_tests_explcitly:
        for key in PROCESSORS:
            results = process_tests(key, prefix, node_list)
            not_tested |= results['not_tested']
            bad_nodes |= results['bad_nodes']

    else:
        if alltoall_rack_tests:
            results = process_tests('alltoall-rack', prefix, node_list)
            not_tested |= results['not_tested']
            bad_nodes |= results['bad_nodes']
        if alltoall_switch_tests:
            results = process_tests('alltoall-switch', prefix, node_list)
            not_tested |= results['not_tested']
            bad_nodes |= results['bad_nodes']
        if alltoall_pair_tests:
            results = process_tests('alltoall-pair', prefix, node_list)
            not_tested |= results['not_tested']
            bad_nodes |= results['bad_nodes']
        if bandwidth_tests:
            results = process_tests('bandwidth', prefix, node_list)
            not_tested |= results['not_tested']
            bad_nodes |= results['bad_nodes']
        if node_tests:
            results = process_tests('node', prefix, node_list)
            not_tested |= results['not_tested']
            bad_nodes |= results['bad_nodes']
    
    not_tested(prefix, node_list, not_tested, bad_nodes)


def process_tests (key, prefix, node_list):
    results = PROCESSORS[key](prefix, node_list)
    log_result_summary(results)
    write_result_files(os.path.join(prefix, key), results)
    return results


def log_result_summary(results):
    all_nodes = (
        set(results['good_nodes'])
        | set(results['bad_nodes'])
        | set(results['not_tested'])
    )
    logger.info('Bad nodes: {0} / {1}'.format(
        len(results['bad_nodes']), len(all_nodes)))
    logger.info('Good nodes: {0} / {1}'.format(
        len(results['good_nodes']), len(all_nodes)))
    logger.info('Untested nodes: {0} / {1}'.format(
        len(results['not_tested']), len(all_nodes)))


def write_result_files(prefix, data):
    bench.util.write_node_list(
        os.path.join(prefix, 'bad_nodes'),
        data['bad_nodes'],
    )

    bench.util.write_node_list(
        os.path.join(prefix, 'bad_not_tested_nodes'),
        (set(data['bad_nodes']) | set(data['not_tested'])),
    )

    bench.util.write_node_list(
        os.path.join(prefix, 'good_nodes'),
        data['good_nodes'],
    )


def not_tested(prefix, node_list, not_tested, bad_nodes):
    not_good_nodes = set(bad_nodes) | set(not_tested)
    good_nodes = set(node_list) - not_good_nodes
    not_in_test = (
        set(node_list)
        - (bad_nodes | good_nodes | not_tested)
    )

    logger.info("Total not tested = " + str(len(not_tested)))
    logger.info("Total bad nodes  = " + str(len(bad_nodes)))
    logger.info("Total good nodes  = " + str(len(good_nodes)))
    logger.info("Total not in test = " + str(len(not_in_test)))

    bench.util.write_node_list(
        os.path.join(prefix, 'not_tested'),
        not_tested,
    )
    bench.util.write_node_list(
        os.path.join(prefix, 'bad_nodes'),
        bad_nodes,
    )
    bench.util.write_node_list(
        os.path.join(prefix, 'not_in_test'),
        not_in_test,
    )
