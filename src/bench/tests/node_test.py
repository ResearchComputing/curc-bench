import bench.framework
import bench.exc
import bench.util
import jinja2
import logging
import os
import pkg_resources
import re


class NodeTest(bench.framework.TestFramework):

    def __init__(self):
        bench.framework.TestFramework.__init__(self)

        self.Add = bench.framework_add.Add(self.logger, self.generate)

        self.TEMPLATE = jinja2.Template(
            pkg_resources.resource_string(__name__, 'node.job'),
            keep_trailing_newline=True,
        )

        self.STREAM_P_T = r'^{0}: *([0-9\.]+) +([0-9\.]+) +([0-9\.]+) +([0-9\.]+) *$'
        self.STREAM_COPY_P = re.compile(self.STREAM_P_T.format('Copy'), flags=re.MULTILINE)
        self.STREAM_SCALE_P = re.compile(self.STREAM_P_T.format('Scale'), flags=re.MULTILINE)
        self.STREAM_ADD_P = re.compile(self.STREAM_P_T.format('Add'), flags=re.MULTILINE)
        self.STREAM_TRIAD_P = re.compile(self.STREAM_P_T.format('Triad'), flags=re.MULTILINE)


    def generate(self, nodes, prefix, topology=None):
        if topology:
            logger.info('node: ignoring topology (not used)')
        for node in nodes:
            test_dir = os.path.join(prefix, node)
            bench.util.mkdir_p(test_dir)

            script_file = os.path.join(test_dir, '{0}.job'.format(node))
            with open(script_file, 'w') as fp:
                fp.write(self.TEMPLATE.render(
                    job_name = 'bench-node-{0}'.format(node),
                    node_name = node,
                ))

            node_list_file = os.path.join(test_dir, 'node_list')
            bench.util.write_node_list(node_list_file, [node])
        self.logger.info('node: add: {0}'.format(len(nodes)))
