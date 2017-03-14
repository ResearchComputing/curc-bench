import bench.util
import collections
import hostlist
import json
import random
import re


SWITCH_NAME_P = re.compile(r'SwitchName=([^ ]+)')
RACK_NAME_P = re.compile(r'RackName=([^ ]+)')
NODES_P = re.compile(r'Nodes=([^ ]+)')
NODE_HOSTNAME_P = re.compile(r'^(.*)node([0-9][0-9])([0-9]+)$')


def parse_topology_conf (topology_file):
    with open(topology_file) as fp:
        for line in fp:
            print("LINE = ", line)
            line = line.rstrip()
            rack_match = RACK_NAME_P.search(line)
            switch_match = SWITCH_NAME_P.search(line)
            if not (switch_match or rack_match):
                continue
            nodes_match = NODES_P.search(line)
            if not nodes_match:
                continue

            nodes = set(hostlist.expand_hostlist(nodes_match.group(1)))

            if rack_match:
                rack_name = rack_match.group(1)
                yield rack_name, nodes

            elif switch_match:
                switch_name = switch_match.group(1)
                yield switch_name, nodes


def get_topology (topology_file):
    return dict(parse_topology_conf(topology_file))

def get_rack_nodes(nodes, topology):
    nodes = set(nodes)
    rack_nodes = collections.defaultdict(set)
    for rack_name, all_rack_nodes in topology.iteritems():
        rack_nodes[rack_name] |= all_rack_nodes & nodes
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
        if len(switch_nodes) < 2:
            continue
        for node_pair in get_node_pairs(switch_nodes):
            key = ','.join(sorted(node_pair))
            switch_node_pairs[key] = node_pair
    return switch_node_pairs


def get_node_pairs(nodes):
    for node_pair in bench.util.chunks(sorted(nodes), 2):
        node_pair = set(node_pair)
        if len(node_pair) == 1:
            node_pair.add(random.choice(list(set(nodes) - set(node_pair))))
        yield node_pair
