import bench.framework
import bench.exc
import bench.util
import jinja2
import logging
import os
import pkg_resources
import re


class AllToAllTest(bench.framework.TestFramework):

    def __init__(self):
        bench.framework.TestFramework.__init__(self)

        self.Add = bench.framework_add.Add(self.logger, self.generate)

        self.TEMPLATE = jinja2.Template(
            pkg_resources.resource_string(__name__, 'alltoall.job'),
            keep_trailing_newline=True,
        )

    def generate(self, nodes, prefix, topology=None, alltoall_type=None):
        if not topology:
            topology = {}
        test_nodes = None
        if alltoall_type == 'alltoall-rack':
            test_nodes = bench.infiniband.get_rack_nodes(nodes, topology)
        elif alltoall_type == 'alltoall-switch':
            test_nodes = bench.infiniband.get_switch_nodes(nodes, topology)
        elif alltoall_type == 'alltoall-pair':
            test_nodes = bench.infiniband.get_switch_node_pairs(nodes, topology)
        for test_name, test_nodes_ in test_nodes.iteritems():
            if test_nodes_:
                test_dir = os.path.join(prefix, test_name)
                self.render(test_dir, test_nodes_, test_name)
        self.logger.info('{ttype}: add: {num_tests}'.format(
                                            ttype=alltoall_type,
                                            num_tests=len(test_nodes)))


    def render(self, prefix, nodes, node_list_name):
        bench.util.mkdir_p(prefix)
        script_file = os.path.join(prefix, '{0}.job'.format(node_list_name))
        with open(script_file, 'w') as fp:
            fp.write(self.TEMPLATE.render(
                job_name = 'bench-alltoall-{0}'.format(node_list_name),
                nodes = list(sorted(nodes)),
            ))

        node_list_file = os.path.join(prefix, 'node_list')
        bench.util.write_node_list(node_list_file, nodes)
