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


def reserve_nodes (prefix, key, bad_nodes=None, not_tested=None):
    bad_nodes_path = os.path.join(prefix, key, 'bad_nodes')
    try:
        bad_nodes_ = set(bench.util.read_node_list(bad_nodes_path))
    except IOError as ex:
        logger.info('unable to read {0}'.format(bad_nodes_path))
        logger.debug(ex, exc_info=True)
        bad_nodes = set()

    not_tested_path = os.path.join(prefix, key, 'not_tested')
    try:
        not_tested_ = set(bench.util.read_node_list(not_tested_path))
    except IOError as ex:
        logger.info('unable to read {0}'.format(not_tested_path))
        logger.debug(ex, exc_info=True)
        not_tested_ = set()

    # by default, reserve bad_nodes and not_tested
    if bad_nodes is None and not_tested is None:
        reserve_nodes_ = bad_nodes_ | not_tested_
    else:
        reserve_nodes_ = set()
        if bad_nodes:
            reserve_nodes_ |= bad_nodes_
        if not_tested:
            reserve_nodes_ |= not_tested_

    if reserve_nodes_:
        try:
            bench.slurm.scontrol(
                'create',
                reservation='bench-{0}'.format(key),
                accounts = 'crcbenchmark',
                flags='overlap',
                starttime='now',
                nodes=','.join(sorted(reserve_nodes_)),
            )
        except bench.exc.SlurmError as ex:
            logger.error(ex)
            logger.debug(ex, exc_info=True)
