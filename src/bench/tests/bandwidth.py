import bench.util.infiniband
import bench.util
import jinja2
import os
import pkg_resources


TEMPLATE = jinja2.Template(
    pkg_resources.resource_string(__name__, 'bandwidth.job'),
    keep_trailing_newline=True,
)


def generate(nodes, topology, prefix):
    switches = bench.util.infiniband.get_switch_nodes(nodes, topology)
    print os.listdir(prefix)
    for switch_name, switch_nodes in switches.iteritems():
        if not switch_nodes:
            continue
        
        print os.listdir(prefix)
        node_pairs = bench.util.infiniband.get_node_pairs(switch_nodes)
        for node_pair in node_pairs.itervalues():
            node_pair = list(sorted(node_pair))
            node_pair_name = ','.join(node_pair)
            test_dir = os.path.join(prefix, node_pair_name)
            bench.util.mkdir_p(test_dir)
            script = os.path.join(test_dir, '{0}.job'.format(node_pair_name))
            with open(script, 'w') as fp:
                fp.write(TEMPLATE.render(
                    job_name = node_pair_name,
                    nodes = node_pair,
                ))
            bench.util.write_node_list(os.path.join(test_dir, 'node_list'), node_pair)
        
    print os.listdir(prefix)
