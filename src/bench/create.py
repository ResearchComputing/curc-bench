from bench.util.hostlist import expand_hostlist
import logging
import os
import pyslurm
import re


logger = logging.getLogger('Benchmarks')


PM_RESERVATIONS_P = re.compile(r'^.*PM-(janus|gpu|himem|serial|ipcc)$')
FREE_NODE_STATES = ('IDLE', 'ALLOCATED', 'COMPLETING', 'RESERVED')


def get_reserved_nodes():
    reserved_nodes = set()
    reservations = pyslurm.reservation()
    for reservation_name, reservation in reservations.get().iteritems():
        if PM_RESERVATIONS_P.match(reservation_name):
            continue
        elif 'node_list' not in reservation:
            continue
        else:
            reserved_nodes.update(set(expand_hostlist(reservation['node_list'])))
    return reserved_nodes


def get_free_nodes():
    nodes = pyslurm.node()
    free_nodes = set(
        node_name for node_name, node in nodes.get().iteritems()
        if 'node_state' in node
        and node['node_state'] in FREE_NODE_STATES)
    return free_nodes


def execute(directory):
    logger.info('creating node list in {0}'.format(directory))

    free_nodes = get_free_nodes()
    logger.info("free nodes: {0}".format(len(free_nodes)))

    reserved_nodes = get_reserved_nodes()
    logger.info("reserved nodes: {0}".format(len(reserved_nodes)))

    targeted_nodes = set(expand_hostlist('node[01-17][01-80]'))

    node_list = (free_nodes - reserved_nodes) & targeted_nodes
    logger.info("nodes to test: {0}".format(len(node_list)))

    node_list_filename = os.path.join(directory, 'node_list')
    try:
        with open(node_list_filename, 'w') as fp:
            for node_name in sorted(node_list):
                fp.write("{0}\n".format(node_name))
    except IOError, ex:
        logger.error("could not write node_list to file: {0}".format(ex))
