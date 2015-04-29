import bench.util
import hostlist
import logging
import os
import pyslurm


logger = logging.getLogger(__name__)


def get_reserved_nodes(reservation_name):
    reservation = pyslurm.reservation().get()[reservation_name]
    return set(hostlist.expand_hostlist(reservation['node_list']))


def get_nodes():
    return set(node_name for node_name in pyslurm.node().get())


def execute(directory,
            include_nodes=None, include_reservation=None,
            exclude_nodes=None, exclude_reservation=None,
):
    node_list_filename = os.path.join(directory, 'node_list')
    logger.info('creating {0}'.format(node_list_filename))

    node_list = get_nodes()

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
