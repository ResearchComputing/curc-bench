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
            node_tests=None,
            **kwargs):

    reserve_any_tests_explicitly = (
        alltoall_rack_tests
        or alltoall_switch_tests
        or alltoall_pair_tests
        or bandwidth_tests
        or node_tests
    )

    if not reserve_any_tests_explicitly:
        reserve_nodes(prefix, 'node', **kwargs)
        reserve_nodes(prefix, 'bandwidth', **kwargs)
        reserve_nodes(prefix, 'alltoall-rack', **kwargs)
        reserve_nodes(prefix, 'alltoall-switch', **kwargs)
        reserve_nodes(prefix, 'alltoall-pair', **kwargs)

    else:
        if alltoall_rack_tests:
            reserve_nodes(prefix, 'alltoall-rack', **kwargs)
        if alltoall_switch_tests:
            reserve_nodes(prefix, 'alltoall-switch', **kwargs)
        if alltoall_pair_tests:
            reserve_nodes(prefix, 'alltoall-pair', **kwargs)
        if bandwidth_tests:
            reserve_nodes(prefix, 'bandwidth', **kwargs)
        if node_tests:
            reserve_nodes(prefix, 'node', **kwargs)


def reserve_nodes (prefix, key, fail_nodes=None, error_nodes=None):
    fail_nodes_path = os.path.join(prefix, key, 'fail_nodes')
    try:
        fail_nodes_ = set(bench.util.read_node_list(fail_nodes_path))
    except IOError as ex:
        logger.info('unable to read {0}'.format(fail_nodes_path))
        logger.debug(ex, exc_info=True)
        fail_nodes_ = set()

    error_nodes_path = os.path.join(prefix, key, 'error_nodes')
    try:
        error_nodes_ = set(bench.util.read_node_list(error_nodes_path))
    except IOError as ex:
        logger.info('unable to read {0}'.format(error_nodes_path))
        logger.debug(ex, exc_info=True)
        error_nodes_ = set()

    # by default, reserve fail_nodes and error_nodes
    if not (fail_nodes or error_nodes):
        reserve_nodes_ = fail_nodes_ | error_nodes_
    else:
        reserve_nodes_ = set()
        if fail_nodes:
            reserve_nodes_ |= fail_nodes_
        if error_nodes:
            reserve_nodes_ |= error_nodes_

    if reserve_nodes_:
        reservation_name = 'bench-{0}'.format(key)
        try:
            bench.slurm.scontrol(
                'create',
                reservation=reservation_name,
                accounts = 'crcbenchmark',
                flags='overlap',
                starttime='now',
                duration='UNLIMITED',
                nodes=','.join(sorted(reserve_nodes_)),
            )
        except bench.exc.SlurmError as ex:
            logger.error(ex)
            logger.debug(ex, exc_info=True)
        else:
            logger.info('{0}: {1}'.format(reservation_name, len(reserve_nodes_)))
