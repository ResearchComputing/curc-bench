import bench.util
import jinja2
import logging
import os
import pkg_resources


logger = logging.getLogger(__name__)


TEMPLATE = jinja2.Template(
    pkg_resources.resource_string(__name__, 'alltoall.job'),
    keep_trailing_newline=True,
)


def generate_alltoall_rack(nodes, prefix):
    rack_nodes = bench.util.infiniband.get_rack_nodes(nodes)
    for rack_name, rack_nodes in rack_nodes.iteritems():
        if rack_nodes:
            render(prefix, rack_nodes, rack_name)


def generate_alltoall_switch(nodes, topology, prefix):
    switch_nodes = bench.util.infiniband.get_switch_nodes(nodes, topology)
    for switch_name, switch_nodes in switch_nodes.iteritems():
        if switch_nodes:
            render(prefix, switch_nodes, switch_name)


def generate_alltoall_pair(nodes, topology, prefix):
    node_pairs = bench.util.infiniband.get_switch_node_pairs(nodes, topology)
    for pair_name, name_list in node_pairs.iteritems():
        if name_list:
            render(prefix, name_list, pair_name)


def render(prefix, nodes, node_list_name):
    output_file = os.path.join(prefix, node_list_name)
    with open(output_file, 'w') as fp:
        fp.write(TEMPLATE.render(
            node_list_name = node_list_name,
            nodes = list(sorted(nodes)),
            num_nodes = len(nodes),
        ))
