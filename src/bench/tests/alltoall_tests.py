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
        self.Submit = bench.framework_submit.Submit(self.logger, test_name)

        self.TEMPLATE = jinja2.Template(
            pkg_resources.resource_string(__name__, 'alltoall.job'),
            keep_trailing_newline=True,
        )


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
            ))

        node_list_file = os.path.join(prefix, 'node_list')
        bench.util.write_node_list(node_list_file, nodes)
