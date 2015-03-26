import bench.util.infiniband
import bench.util
import bench.util.util
import jinja2
import os
import pkg_resources


TEMPLATE = jinja2.Template(
    pkg_resources.resource_string(__name__, 'bandwidth.job'),
    keep_trailing_newline=True,
)


def generate(nodes, prefix):
    switches = bench.util.infiniband.rack_switch_18(nodes)
    for switch_name, switch_nodes in switches.iteritems():
        if not switch_nodes:
            continue
        node_pairs = bench.util.infiniband.rack_list_subsets(switch_nodes)
        for node_pair in node_pairs.itervalues():
            node_pair = list(sorted(node_pair))
            job_name = '-'.join(node_pair)
            output_file = os.path.join(prefix, '{0}.job'.format(job_name))
            with open(output_file, 'w') as fp:
                fp.write(TEMPLATE.render(
                    job_name = job_name,
                    nodes = node_pair,
                ))
