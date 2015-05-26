import bench.util
import hostlist
import logging
import os
import pyslurm


logger = logging.getLogger(__name__)


def get_reserved_nodes(reservation_name):
    reservation = pyslurm.reservation().get()[reservation_name]
    return set(hostlist.expand_hostlist(reservation['node_list']))


def get_nodes(include_states=None, exclude_states=None):
    if include_states:
        include_states = set(state.lower() for state in include_states)
    if exclude_states:
        exclude_states = set(state.lower() for state in exclude_states)
    nodes = pyslurm.node().get().itervalues()
    if include_states:
        nodes = (node for node in nodes
                 if node['node_state'].rstrip('*').lower()
                 in include_states)
    if exclude_states:
        nodes = (node for node in nodes
                 if node['node_state'].rstrip('*').lower()
                 not in exclude_states)
    return set(node['name'] for node in nodes)


def execute(directory,
            include_nodes=None,
            exclude_nodes=None,

            include_reservation=None,
            exclude_reservation=None,

            include_states=None,
            exclude_states=None,
):
    node_list_filename = os.path.join(directory, 'node_list')
    logger.info('creating {0}'.format(node_list_filename))

    all_nodes = get_nodes()

    if include_states is None and exclude_states is None:
        exclude_states = ['down', 'draining', 'drained']

    node_list = get_nodes(
        include_states=include_states,
        exclude_states=exclude_states,
    )

    if include_nodes is not None or include_reservation is not None:
        include_nodes_ = set()
        if include_nodes is not None:
            include_nodes_ |= set(hostlist.expand_hostlist(include_nodes))
        if include_reservation is not None:
            include_nodes_ |= get_reserved_nodes(include_reservation)
        node_list = node_list & include_nodes_

    if exclude_nodes is not None or exclude_reservation is not None:
        exclude_nodes_ = set()
        if exclude_nodes is not None:
            exclude_nodes_ |= set(hostlist.expand_hostlist(exclude_nodes))
        if exclude_reservation is not None:
            exclude_nodes_ |= get_reserved_nodes(exclude_reservation)
        node_list = node_list - exclude_nodes_

    logger.info('nodes to test: {0}'.format(len(node_list)))

    try:
        bench.util.write_node_list(node_list_filename, sorted(node_list))
    except IOError, ex:
        logger.error('unable to write {0}'.format(node_list_filename))
        logger.debug(ex, exc_info=True)

    not_tested_filename = os.path.join(directory, 'not_tested')
    not_tested_nodes = all_nodes - node_list
    if not_tested_nodes:
        logger.warn('not tested: {0} ({1} nodes)'.format(
            hostlist.collect_hostlist(not_tested_nodes),
            len(not_tested_nodes),
        ))
    try:
        bench.util.write_node_list(not_tested_filename, sorted(not_tested_nodes))
    except IOError, ex:
        logger.error('unable to write {0}'.format(not_tested_filename))
        logger.debug(ex, exc_info=True)
