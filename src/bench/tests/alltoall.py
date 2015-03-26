import bench.util
import bench.util.util
import jinja2
import os
import pkg_resources


TEMPLATE = jinja2.Template(
    pkg_resources.resource_string(__name__, 'alltoall.job'),
    keep_trailing_newline=True,
)


def generate_allrack(nodes, reservation_name, prefix):
    rack_nodes = bench.util.infiniband.rack(nodes)
    for rack_name, rack_nodes in rack_nodes.iteritems():
        if rack_nodes:
            render(prefix, reservation_name, rack_nodes, rack_name)


def generate_allswitch(nodes, reservation_name, prefix):
    switch_nodes = bench.util.infiniband.rack_switch_18(nodes)
    for switch_name, switch_nodes in switch_nodes.iteritems():
        if switch_nodes:
            render(prefix, reservation_name, switch_nodes, switch_name)


def generate_allpair(nodes, reservation_name, prefix):
    node_pairs = bench.util.infiniband.rack_switch_pairs(nodes)
    for pair_name, name_list in node_pairs.iteritems():
        if name_list:
            render(prefix, reservation_name, name_list, pair_name)


def render(prefix, reservation_name, nodes, node_list_name):
    output_file = os.path.join(prefix, node_list_name)
    with open(output_file, 'w') as fp:
        fp.write(TEMPLATE.render(
            reservation_name = reservation_name,
            id_ = node_list_name,
            nodes = nodes,
            num_nodes = len(nodes),
        ))
