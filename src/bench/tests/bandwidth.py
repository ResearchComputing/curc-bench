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


def generate(node_list, reservation_name, prefix):
    switches = bench.util.infiniband.rack_switch_18(node_list)
    rack_list = []
    for switch_name, switch_node_list in switches.iteritems():
        if not switch_node_list:
            continue
        node_pairs = bench.util.infiniband.rack_list_subsets(switch_node_list)
        for node_pair in node_pairs.itervalues():
            node_list = ','.join(node_pair)
            job_name = '-'.join(node_pair)
            output_file = os.path.join(prefix, '{0}.job'.format(job_name))
            with open(output_file, 'w') as fp:
                fp.write(TEMPLATE.render(
                    job_name = job_name,
                    reservation_name = reservation_name,
                    node_list = node_list,
                ))
