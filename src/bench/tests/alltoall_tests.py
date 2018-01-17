import bench.framework
import bench.exc
import bench.util
import bench.configuration as bc
import jinja2
import logging
import os
import pkg_resources
import hostlist
import collections

class AllToAllTest(bench.framework.TestFramework):

    def __init__(self, test_name):
        bench.framework.TestFramework.__init__(self, test_name)

        self.Add = bench.framework_add.Add(self.logger, self.generate, test_name)

        self.subtests = [test_name]

        self.Submit = bench.framework_submit.Submit(self.logger, test_name)
        self.Process = bench.framework_process.Process(self.logger, self.parse_data, self.evaluate_data, test_name, self.subtests)
        self.Reserve = bench.framework_reserve.Reserve(self.logger, test_name)

        self.TEMPLATE = jinja2.Template(
            pkg_resources.resource_string(__name__, 'alltoall.job'),
            keep_trailing_newline=True,
        )

        # additional latency above the specified limit allowed
        self.latency_max_percent = 1.55

        # expected average osu_alltoall latency for each node count
        self.expected_latencies = { 2:13613.5219632, 3:28375.5187868,
                               4:43137.5156105, 5:57899.5124341,
                               6:72661.5092577, 7:87423.5060814,
                               8:102185.502905, 9:116947.499729,
                               10:131709.496552, 11:146471.493376,
                               12:161233.4902, 13:175995.487023,
                               14:190757.483847, 15:205519.480671,
                               16:220281.477494, 17:235043.474318,
                               18:249805.471141, 19:264567.467965,
                               20:279329.464789, 21:294091.461612,
                               22:308853.458436, 23:323615.45526,
                               24:338377.452083, 25:353139.448907,
                               26:367901.445731, 27:382663.442554,
                               28:397425.439378, 29:412187.436202,
                               30:426949.433025, 31:441711.429849,
                               32:456473.426672, 33:471235.423496,
                               34:753806.42032, 35:753806.417143,
                               36:753806.413967, 37:753806.410791,
                               38:753806.407614, 39:753806.404438,
                               40:753806.401262, 50:456062.014488,
                               51:522754.035136, 52:589446.055784,
                               53:656138.076432, 54:722830.09708,
                               55:789522.117728, 56:856214.138376,
                               57:922906.159024, 58:989598.179672,
                               59:1056290.20032, 60:1122982.22097,
                               61:1189674.24162, 62:1256366.26226,
                               63:1323058.28291, 64:1389750.30356,
                               65:1456442.32421, 66:1523134.34486,
                               67:1589826.3655, 68:1656518.38615,
                               69:1723210.4068, 70:1789902.42745,
                               71:1856594.4481, 72:1923286.46874,
                               73:1989978.48939, 74:2056670.51004,
                               75:2123362.53069, 76:2190054.55134,
                               77:2256746.57198, 78:2323438.59263,
                               79:2390130.61328, 80:2456822.63393, }


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
                osu_alltoall_path = bc.config['alltoall']['osu'],
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
            return False
        average_latency = 1.0 * sum(datum[1] for datum in data) / len(data)
        if num_nodes not in self.expected_latencies:
            self.logger.debug('alltoall: {0}: {1}: average {2}, not defined'.format(
                subtest, num_nodes, average_latency))
            return False
        elif average_latency > (self.latency_max_percent * self.expected_latencies[num_nodes]):
            self.logger.debug('alltoall: {0}: {1}: expected {2}, found {3} ({4:.0%})'.format(
                subtest, num_nodes, self.expected_latencies[num_nodes], average_latency,
                average_latency / self.expected_latencies[num_nodes]))
            return False
        else:
            return True
