import errno
import hostlist
import os
import pyslurm


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
    for i in xrange(0, len(l), n):
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
    with open(path, 'w') as fp:
        for node in sorted(nodes):
            fp.write('{0}\n'.format(node))


def filter_node_list (nodes,
                      include_nodes=None,
                      exclude_nodes=None,

                      include_reservations=None,
                      exclude_reservations=None,

                      include_states=None,
                      exclude_states=None,

                      include_files=None,
                      exclude_files=None,
):
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

        # Maintenance reservations shadow node state with MAINT*,
        # making it impossible to detect state DOWN, etc. Treat nodes
        # that have a "reason" as though they are down for purposes of
        # exclusion.
        if 'down' in exclude_states:
            nodes = (node for node in nodes
                     if not node.get('reason'))
    return set(node['name'] for node in nodes)
