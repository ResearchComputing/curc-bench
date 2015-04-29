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


def update_nodes_from_tests (prefix, test_type, down=False):
    bad_nodes_path = os.path.join(prefix, test_type, 'bad_nodes')
    try:
        bad_nodes = set(bench.util.read_node_list(bad_nodes_path))
    except IOError as ex:
        logger.info('update-nodes: file not found: {0}'.format(bad_nodes_path))
        return

    if down:
        node_state = pyslurm.NODE_STATE_DOWN
        node_state_s = 'DOWN'
    else:
        node_state = pyslurm.NODE_STATE_DRAIN
        node_state_s = 'DRAIN'

    pyslurm_node = pyslurm.node()

    if bad_nodes:
        for node in bad_nodes:
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
                logger.error('update-nodes: {0}'.format(
                    pyslurm.slurm_strerror(pyslurm.slurm_get_errno())))
            else:
                logger.info('update-nodes: {0}: {1}'.format(
                    node, node_state_s))
