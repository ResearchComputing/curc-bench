import bench.util
import logging
import pyslurm
import os


logger = logging.getLogger(__name__)


def update_nodes (
        prefix,
        alltoall_rack_tests=None,
        alltoall_switch_tests=None,
        alltoall_pair_tests=None,
        bandwidth_tests=None,
        node_tests=None,
        **kwargs
):
    use_any_tests_explicitly = (
        alltoall_rack_tests
        or alltoall_switch_tests
        or alltoall_pair_tests
        or bandwidth_tests
        or node_tests)

    if not use_any_tests_explicitly:
        update_nodes_from_tests(prefix, 'node', **kwargs)
        update_nodes_from_tests(prefix, 'bandwidth', **kwargs)
        update_nodes_from_tests(prefix, 'alltoall-pair', **kwargs)
        update_nodes_from_tests(prefix, 'alltoall-switch', **kwargs)
        update_nodes_from_tests(prefix, 'alltoall-rack', **kwargs)
    else:
        if node_tests:
            update_nodes_from_tests(prefix, 'node', **kwargs)
        if bandwidth_tests:
            update_nodes_from_tests(prefix, 'bandwidth', **kwargs)
        if alltoall_pair_tests:
            update_nodes_from_tests(prefix, 'alltoall-pair', **kwargs)
        if alltoall_switch_tests:
            update_nodes_from_tests(prefix, 'alltoall-switch', **kwargs)
        if alltoall_rack_tests:
            update_nodes_from_tests(prefix, 'alltoall-rack', **kwargs)


def update_nodes_from_tests (prefix, test_type, fail_nodes=None,
                             error_nodes=None, down=False):
    fail_nodes_path = os.path.join(prefix, test_type, 'fail_nodes')
    try:
        fail_nodes_ = set(bench.util.read_node_list(fail_nodes_path))
    except IOError as ex:
        logger.info('unable to read {0}'.format(fail_nodes_path))
        logger.debug(ex, exc_info=True)
        fail_nodes_ = set()

    error_nodes_path = os.path.join(prefix, test_type, 'error_nodes')
    try:
        error_nodes_ = set(bench.util.read_node_list(error_nodes_path))
    except IOError as ex:
        logger.info('unable to read {0}'.format(error_nodes_path))
        logger.debug(ex, exc_info=True)
        error_nodes_ = set()

    # by default, reserve fail_nodes and error_nodes
    if not (fail_nodes or error_nodes):
        nodes_to_update = fail_nodes_ | error_nodes_
    else:
        nodes_to_update = set()
        if fail_nodes:
            nodes_to_update |= fail_nodes_
        if error_nodes:
            nodes_to_update |= error_nodes_

    if down:
        node_state = pyslurm.NODE_STATE_DOWN
        node_state_s = 'DOWN'
    else:
        node_state = pyslurm.NODE_STATE_DRAIN
        node_state_s = 'DRAINED'

    pyslurm_node = pyslurm.node()

    for node in sorted(nodes_to_update):
        current_node_state = pyslurm_node.find_id(node)['node_state']
        if current_node_state.startswith(node_state_s):
            continue
        node_update = {
            'node_names': node,
            'node_state': node_state,
            'reason': 'bench:{0}'.format(test_type),
        }
        rc = pyslurm_node.update(node_update)
        if rc != 0:
            logger.error('unable to update node {0}: {1}'.format(
                node,
                pyslurm.slurm_strerror(pyslurm.slurm_get_errno())
            ))
        else:
            logger.info('{0} set to {1}'.format(
                node, node_state_s))
