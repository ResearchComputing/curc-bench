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
import random


class AllToAllTest(bench.framework.TestFramework):

    def __init__(self, test_name):
        bench.framework.TestFramework.__init__(self, test_name)

        self.Add = bench.framework_add.Add(self.logger, self.generate, test_name)

        self.TEMPLATE = jinja2.Template(
            pkg_resources.resource_string(__name__, 'alltoall.job'),
            keep_trailing_newline=True,
        )


    def generate(self, nodes, prefix, topology=None):

        if not topology:
            topology = {}
        test_nodes = None

        if self.test_name == 'alltoall-rack':
            test_nodes = self.get_alltoall_nodes(nodes, 'Rack')
        elif self.test_name == 'alltoall-switch':
            test_nodes = self.get_alltoall_nodes(nodes, 'Switch')
        elif self.test_name == 'alltoall-pair':
            test_nodes = self.get_alltoall_nodes(nodes, 'Pair')

        # Write job scripts for each test
        for test_name, test_nodes_ in test_nodes.iteritems():
            if test_nodes_:
                test_dir = os.path.join(prefix, test_name)
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


    def get_alltoall_nodes(self, nodes, alltoall_type):
        '''nodes = testable node list, alltoall_type = a string: 'Rack', 'Switch', 'Pair'
        Returns: dictionary consisting of hardware name as key and set of testable nodes as value'''

        if alltoall_type == 'Rack' or alltoall_type == 'Switch':
            node_set = collections.defaultdict(set)
            for hardware_name in bc.config['alltoall'][alltoall_type]:
                node_set[hardware_name] = set(hostlist.expand_hostlist(bc.config['alltoall'][alltoall_type][hardware_name]))
                node_set[hardware_name] &= set(nodes)  #Don't include error/excluded nodes
            return node_set
        elif alltoall_type == 'Pair':
            node_set = collections.defaultdict(set)
            for switch_name, switch_nodes in bc.config['alltoall']['Switch'].iteritems():
                switch_nodes = set(hostlist.expand_hostlist(switch_nodes))
                switch_nodes &= set(nodes)  #Don't include error/excluded nodes
                if len(switch_nodes) < 2:
                    continue
                for node_pair in self.get_node_pairs(switch_nodes):
                    key = ','.join(sorted(node_pair))
                    node_set[key] = node_pair
            return node_set


    def get_node_pairs(self, nodes):
        for node_pair in bench.util.chunks(sorted(nodes), 2):
            node_pair = set(node_pair)
            if len(node_pair) == 1:
                node_pair.add(random.choice(list(set(nodes) - set(node_pair))))
            yield node_pair
