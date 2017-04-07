import bench.framework
import bench.exc
import bench.util
import bench.configuration as bc
import jinja2
import logging
import os
import pkg_resources
import re


class BandwidthTest(bench.framework.TestFramework):

    def __init__(self, test_name):
        bench.framework.TestFramework.__init__(self, test_name)

        self.Add = bench.framework_add.Add(self.logger, self.generate, test_name)

        self.TEMPLATE = jinja2.Template(
            pkg_resources.resource_string(__name__, 'bandwidth.job'),
            keep_trailing_newline=True,
        )

    def generate(self, nodes, prefix, topology=None):

        if not topology:
            topology = {}
        node_pairs = bench.util.get_test_nodes(nodes, 'Pair')

        for pair_name, node_pair in node_pairs.iteritems():
            test_dir = os.path.join(prefix, "tests", pair_name)
            bench.util.mkdir_p(test_dir)
            script = os.path.join(test_dir, '{0}.job'.format(pair_name))
            with open(script, 'w') as fp:
                fp.write(self.TEMPLATE.render(
                    job_name = 'bench-bandwidth-{0}'.format(pair_name),
                    nodes = node_pair,
                    osu_bw_path = bc.config['bandwidth']['osu'],
                ))
            bench.util.write_node_list(os.path.join(test_dir, 'node_list'), node_pair)
        self.logger.info('bandwidth: add: {0}'.format(len(node_pairs)))
