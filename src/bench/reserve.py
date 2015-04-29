import bench.exc
import bench.slurm
import bench.util
import os
import time

import logging
logger = logging.getLogger(__name__)


def execute(prefix,
            alltoall_rack_tests=None,
            alltoall_switch_tests=None,
            alltoall_pair_tests=None,
            bandwidth_tests=None,
            node_tests=None):

    reserve_any_tests_explicitly = (
        alltoall_rack_tests
        or alltoall_switch_tests
        or alltoall_pair_tests
        or bandwidth_tests
        or node_tests)

    if not reserve_any_tests_explicitly:
        bench.util.log_error(lambda: reserve_bad_nodes(prefix, 'node'))
        bench.util.log_error(lambda: reserve_bad_nodes(prefix, 'bandwidth'))
        bench.util.log_error(lambda: reserve_bad_nodes(prefix, 'alltoall-rack'))
        bench.util.log_error(lambda: reserve_bad_nodes(prefix, 'alltoall-switch'))
        bench.util.log_error(lambda: reserve_bad_nodes(prefix, 'alltoall-pair'))

    else:
        if alltoall_rack_tests:
            bench.util.log_error(lambda: reserve_bad_nodes(prefix, 'alltoall-rack'))
        if alltoall_switch_tests:
            bench.util.log_error(lambda: reserve_bad_nodes(prefix, 'alltoall-switch'))
        if alltoall_pair_tests:
            bench.util.log_error(lambda: reserve_bad_nodes(prefix, 'alltoall-pair'))
        if bandwidth_tests:
            bench.util.log_error(lambda: reserve_bad_nodes(prefix, 'bandwidth'))
        if node_tests:
            bench.util.log_error(lambda: reserve_bad_nodes(prefix, 'node'))


def reserve_bad_nodes(prefix, key):
    bad_nodes = set(bench.util.read_node_list(os.path.join(prefix, key, 'bad_nodes')))
    if bad_nodes:
        result = bench.slurm.scontrol(
            'create',
            reservation='bench-{0}'.format(key),
            accounts = 'crcbenchmark',
            flags='overlap',
            starttime='now',
            nodes=','.join(bad_nodes),
        )
        return result
