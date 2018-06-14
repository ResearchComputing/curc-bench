import bench.framework
import bench.exc
import bench.util
import bench.conf.bandwidth_conf as bbc
import jinja2
import logging
import os
import pkg_resources
import re


class BandwidthTest(bench.framework.TestFramework):

    def __init__(self, test_name):
        bench.framework.TestFramework.__init__(self, test_name)

        self.subtests = ['osu_bw']

        self.Add = bench.framework_add.Add(self.logger, self.generate, test_name, bbc.config['nodes'])
        self.Submit = bench.framework_submit.Submit(self.logger, test_name)
        self.Process = bench.framework_process.Process(self.logger, self.parse_data, self.evaluate_data, test_name, self.subtests)
        self.Reserve = bench.framework_reserve.Reserve(self.logger, test_name)

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
                    modules = " ".join(bbc.config['modules']),
                    nodes = node_pair,
                    osu_bw_path = bbc.config['osu_bw_path'],
                ))
            bench.util.write_node_list(os.path.join(test_dir, 'node_list'), node_pair)
        self.logger.info('bandwidth: add: {0}'.format(len(node_pairs)))


    def parse_data(self, output, subtest):
        data = {}
        for line in output.splitlines():
            if line.startswith('#'):
                continue
            size, bandwidth = line.strip().split()
            size = int(size)
            bandwidth = float(bandwidth)
            data[size] = bandwidth
        return data


    def evaluate_data(self, data, subtest, *args):
        expected_bandwidths = bbc.config['osu_bandwidths']

        for size, bandwidth in expected_bandwidths.iteritems():
            if size not in data:
                self.logger.debug('bandwidth: {0}: {1}: expected {2}, not found'.format(
                    subtest, size, expected_bandwidths[size]))
                return False, []
            if data[size] < expected_bandwidths[size]:
                self.logger.debug('bandwidth: {0}: {1}: expected {2}, found {3} ({4:.0%})'.format(
                    subtest, size, expected_bandwidths[size], data[size],
                    data[size] / expected_bandwidths[size]))
                return False, [[subtest.split(','), size], data[size], expected_bandwidths[size],
                    data[size] / expected_bandwidths[size]]
        return True, []
