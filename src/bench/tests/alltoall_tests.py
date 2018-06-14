import bench.framework
import bench.exc
import bench.util
import bench.conf.alltoall_conf as bac
import jinja2
import logging
import os
import pkg_resources
import hostlist
import collections

class AllToAllTest(bench.framework.TestFramework):

    def __init__(self, test_name):
        bench.framework.TestFramework.__init__(self, test_name)

        self.Add = bench.framework_add.Add(self.logger, self.generate, test_name, bac.config['nodes'])

        self.subtests = [test_name]

        self.Submit = bench.framework_submit.Submit(self.logger, test_name)
        self.Process = bench.framework_process.Process(self.logger, self.parse_data, self.evaluate_data, test_name, self.subtests)
        self.Reserve = bench.framework_reserve.Reserve(self.logger, test_name)

        self.TEMPLATE = jinja2.Template(
            pkg_resources.resource_string(__name__, 'alltoall.job'),
            keep_trailing_newline=True,
        )

        # additional latency above the specified limit allowed
        self.latency_max_percent = bac.config['latency_factor']

        # expected average osu_alltoall latency for each node count
        self.expected_latencies = bac.config['osu_latencies']


    def generate(self, nodes, prefix, topology=None):

        if not topology:
            topology = {}
        test_nodes = None

        if self.test_name == 'alltoall-rack':
            test_nodes = bench.util.get_test_nodes(nodes, 'Rack')
        elif self.test_name == 'alltoall-switch':
            test_nodes = bench.util.get_test_nodes(nodes, 'Switch')
        elif self.test_name == 'alltoall-pair':
            test_nodes = bench.util.get_test_nodes(nodes, 'Pair')

        # Write job scripts for each test
        for test_name, test_nodes_ in test_nodes.iteritems():
            if test_nodes_:
                test_dir = os.path.join(prefix, "tests", test_name)
                self.render(test_dir, test_nodes_, test_name)
        self.logger.info('{ttype}: add: {num_tests}'.format(
                                            ttype=self.test_name,
                                            num_tests=len(test_nodes)))


    def render(self, prefix, nodes, node_list_name):
        bench.util.mkdir_p(prefix)
        script_file = os.path.join(prefix, '{0}.job'.format(node_list_name))
        with open(script_file, 'w') as fp:
            fp.write(self.TEMPLATE.render(
                job_name = 'bench-alltoall-{0}'.format(node_list_name),
                nodes = list(sorted(nodes)),
                modules = " ".join(bac.config['modules']),
                osu_alltoall_path = bac.config['osu_a2a_path'],
                subtest = self.test_name
            ))

        node_list_file = os.path.join(prefix, 'node_list')
        bench.util.write_node_list(node_list_file, nodes)


    def parse_data(self, output, subtest):
        for line in output.splitlines():
            if not line or line.startswith('#'):
                continue

            size, average, min_, max_, iterations = line.split()
            size = int(size)
            average = float(average)
            min_ = float(min_)
            max_ = float(max_)
            iterations = int(iterations)

            yield size, average, min_, max_, iterations



    def evaluate_data (self, data, subtest, test_nodes):
        data = list(data)
        num_nodes = len(test_nodes)
        if len(data) <= 0:
            return False, []
        average_latency = 1.0 * sum(datum[1] for datum in data) / len(data)
        if num_nodes not in self.expected_latencies:
            self.logger.debug('alltoall: {0}: {1}: average {2}, not defined'.format(
                subtest, num_nodes, average_latency))
            return False, []
        elif average_latency > (self.latency_max_percent * self.expected_latencies[num_nodes]):
            self.logger.debug('alltoall: {0}: {1}: expected {2}, found {3} ({4:.0%})'.format(
                subtest, num_nodes, self.expected_latencies[num_nodes], average_latency,
                average_latency / self.expected_latencies[num_nodes]))
            return False, [[subtest, num_nodes], average_latency, self.expected_latencies[num_nodes],
                average_latency / self.expected_latencies[num_nodes]]
        else:
            return True, []
