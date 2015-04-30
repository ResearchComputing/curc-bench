import bench.util
import collections
import hostlist
import json
import re


SWITCH_NAME_P = re.compile(r'SwitchName=([^ ]+)')
NODES_P = re.compile(r'Nodes=([^ ]+)')


def parse_topology_conf (topology_file):
    with open(topology_file) as fp:
        for line in fp:
            line = line.rstrip()
            switch_match = SWITCH_NAME_P.search(line)
            if not switch_match:
                continue
            nodes_match = NODES_P.search(line)
            if not nodes_match:
                continue
            switch_name = switch_match.group(1)
            nodes = set(hostlist.expand_hostlist(nodes_match.group(1)))
            yield switch_name, nodes


def get_topology (topology_file):
    return dict(parse_topology_conf(topology_file))


def get_rack_nodes(nodes):
    rack_nodes = collections.defaultdict(set)
    for node in nodes:
        rack_num = node[4:6]
        rack_name = 'rack_{0}'.format(rack_num)
        rack_nodes[rack_name].add(node)
    return rack_nodes


def get_switch_nodes(nodes, topology):
    nodes = set(nodes)
    switch_nodes = collections.defaultdict(set)
    for switch_name, all_switch_nodes in topology.iteritems():
        switch_nodes[switch_name] |= all_switch_nodes & nodes
    return switch_nodes


def get_switch_node_pairs(nodes, topology):
    switch_node_pairs = {}
    switches = get_switch_nodes(nodes, topology)
    for switch_name, switch_nodes in switches.iteritems():
        switch_node_pairs.update(get_node_pairs(switch_nodes))
    return switch_node_pairs


def get_node_pairs(nodes):
    data = {}
    for node_pair in bench.util.chunks(sorted(nodes), 2):
        try:
            key = '{0},{1}'.format(*list(sorted(node_pair)))
        except IndexError:
            # odd-length list might end with a single node
            continue
        else:
            data[key] = node_pair
    return data
