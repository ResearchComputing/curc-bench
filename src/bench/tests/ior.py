import bench.framework
import bench.exc
import bench.util
import bench.configuration as bc
import jinja2
import logging
import os
import pkg_resources
import re
import collections
import hostlist


class IorTest(bench.framework.TestFramework):

    def __init__(self, test_name):
        bench.framework.TestFramework.__init__(self, test_name)

        self.Add = bench.framework_add.Add(self.logger, self.generate, test_name)
        self.Submit = bench.framework_submit.Submit(self.logger, test_name)
        self.Process = bench.framework_process.Process(self.logger, self.parse_data, self.evaluate_data, test_name)
        self.Reserve = bench.framework_reserve.Reserve(self.logger, test_name)

        self.TEMPLATE = jinja2.Template(
            pkg_resources.resource_string(__name__, 'ior.job'),
            keep_trailing_newline=True,
        )



    def generate(self, nodes, prefix, topology=None, test_name=None):

        if topology:
            self.logger.info('node: ignoring topology (not used)')

        test_dir = os.path.join(prefix, "tests/ior")
        bench.util.mkdir_p(test_dir)

        script_file = os.path.join(test_dir, '{0}.job'.format('ior'))
        with open(script_file, 'w') as fp:
            fp.write(self.TEMPLATE.render(
                job_name = 'bench-ior',
                ior_path = bc.config['ior']['ior'],
                modules = " ".join(bc.config['ior']['modules'])
            ))

        node_list_file = os.path.join(test_dir, 'node_list')
        bench.util.write_node_list(node_list_file, [''])
        self.logger.info('ior: adding ior test')

    def parse_data(self, output):
        return

    def evaluate_data(self, data, *args):
        return



#
