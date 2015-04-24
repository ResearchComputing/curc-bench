import bench.exc
import bench.util
import os
import pyslurm
import time

import logging
logger = logging.getLogger(__name__)


def execute(prefix,
            alltoall_rack_tests=None,
            alltoall_switch_tests=None,
            alltoall_pair_tests=None,
            bandwidth_tests=None,
            node_tests=None):
    logger.info(prefix)

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
        reservation = pyslurm.create_reservation_dict()
        reservation['accounts'] = 'crcbenchmark'
        reservation['flags'] = 16384 # 'OVERLAP'
        reservation['start_time'] = time.time()
        reservation['name'] = 'bench-{0}'.format(key)
        reservation['node_list'] = ','.join(bad_nodes)
        reservation['node_cnt'] = len(bad_nodes)
        result = pyslurm.slurm_create_reservation(reservation)
        errno = pyslurm.slurm_get_errno()
        if errno != 0:
            strerror = pyslurm.slurm_strerror(errno)
            raise bench.exc.SlurmError(strerror)
        return result
