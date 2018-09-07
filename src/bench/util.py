import errno
import hostlist
import os
import pyslurm
import bench.conf.alltoall_conf as bac
import collections
import random
import bench

def mkdir_p (path):
    try:
        os.makedirs(path)
    except OSError as ex:
        if ex.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    l = list(l)
    for i in range(0, len(l), n):
        yield l[i:i+n]


def read_node_list(node_list_path):
    nodes = []
    with open(node_list_path) as fp:
        for line in fp:
            node = line.strip()
            if node:
                nodes.append(node)
    return nodes


def write_node_list (path, nodes):
    '''nodes - list of string nodenames'''
    with open(path, 'w') as fp:
        for node in sorted(nodes):
            fp.write('{0}\n'.format(node))


def filter_node_list(nodes,
                      include_nodes=None,
                      exclude_nodes=None,
                      include_reservations=None,
                      exclude_reservations=None,
                      include_states=None,
                      exclude_states=None,
                      include_files=None,
                      exclude_files=None,
):
    '''
    nodes=possible nodes to test based on nodes in configuration file
       '''
    nodes = set(nodes)
    if include_states or exclude_states:
        nodes &= set(get_nodes(
            include_states=include_states,
            exclude_states=exclude_states,
        ))
    if include_nodes or include_reservations or include_files:
        include_nodes_ = set()
        if include_nodes:
            for hostlist_ in include_nodes:
                include_nodes_ |= set(hostlist.expand_hostlist(hostlist_))
        if include_reservations:
            for reservation in include_reservations:
                include_nodes_ |= get_reserved_nodes(reservation)
        if include_files:
            for include_file in include_files:
                include_nodes_ |= set(read_node_list(include_file))
        nodes &= include_nodes_
    if exclude_nodes or exclude_reservations or exclude_files:
        exclude_nodes_ = set()
        if exclude_nodes:
            for hostlist_ in exclude_nodes:
                exclude_nodes_ |= set(hostlist.expand_hostlist(hostlist_))
        if exclude_reservations:
            for reservation in exclude_reservations:
                exclude_nodes_ |= get_reserved_nodes(reservation)
        if exclude_files:
            for exclude_file in exclude_files:
                exclude_nodes_ |= set(read_node_list(exclude_file))
        nodes -= exclude_nodes_

    return nodes


def get_reserved_nodes(reservation_name):
    try:
        reservation = pyslurm.reservation().get()[reservation_name]
        return set(hostlist.expand_hostlist(reservation['node_list']))
    except KeyError as ex:
        message = '\nSlurm reservation \'{res}\' doesn\'t exist.\n'.format(res=reservation_name)
        print(message)
        return set()
    return set()


def get_nodes(include_states=None, exclude_states=None):
    if include_states:
        include_states = set(state.lower() for state in include_states)
    if exclude_states:
        exclude_states = set(state.lower() for state in exclude_states)
    nodes = list(pyslurm.node().get().values())
    if include_states:
        nodes = list(node for node in nodes
                 if node['state'].rstrip('*').lower()
                 in include_states)
    if exclude_states:
        nodes = list(node for node in nodes
                 if node['state'].rstrip('*').lower()
                 not in exclude_states)

        # Maintenance reservations shadow node state with MAINT*,
        # making it impossible to detect state DOWN, etc. Treat nodes
        # that have a "reason" as though they are down for purposes of
        # exclusion.
        if 'down' in exclude_states:
            nodes = list(node for node in nodes
                     if not node.get('reason'))
    return set(node['name'] for node in nodes)

def get_test_nodes(nodes, test_type):
    '''nodes = testable node list, test_type = a string: 'Rack', 'Switch', 'Pair'
    Returns: dictionary consisting of hardware name as key and set of testable nodes as value'''

    if test_type == 'Rack' or test_type == 'Switch':
        node_set = collections.defaultdict(set)
        for hardware_name in bac.config[test_type]:
            node_set[hardware_name] = set(hostlist.expand_hostlist(bac.config[test_type][hardware_name]))
            node_set[hardware_name] &= set(nodes)  #Don't include error/excluded nodes
        return node_set
    elif test_type == 'Pair':
        node_set = collections.defaultdict(set)
        for switch_name, switch_nodes in bac.config['Switch'].items():
            switch_nodes = set(hostlist.expand_hostlist(switch_nodes))
            switch_nodes &= set(nodes)  #Don't include error/excluded nodes
            if len(switch_nodes) < 2:
                continue
            for node_pair in get_node_pairs(switch_nodes):
                key = ','.join(sorted(node_pair))
                node_set[key] = node_pair
        return node_set


def get_node_pairs(nodes):
    for node_pair in chunks(sorted(nodes), 2):
        node_pair = set(node_pair)
        if len(node_pair) == 1:
            node_pair.add(random.choice(list(set(nodes) - set(node_pair))))
        yield node_pair
