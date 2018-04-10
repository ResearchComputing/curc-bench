import bench.framework
import bench.tests.node_test
import bench.tests.bandwidth_test
import bench.tests.alltoall_tests
import bench.tests.ior
import bench.util
import hostlist
import mock
import os
import pkg_resources
import re
import shutil
import tempfile
import unittest
import jinja2


class TestProcess(unittest.TestCase):

    def assertIsFile (self, path):
        assert os.path.isfile(path), '{0} does not exist'.format(path)

    def setUp (self):
        self.directory = tempfile.mkdtemp()
        self.node_dir = os.path.join(self.directory, 'node')
        self.node_test_dir = os.path.join(self.node_dir, 'tests')

        os.mkdir(self.node_dir)
        os.mkdir(self.node_test_dir)

        self.num_nodes = 11

        self.nodes = ['tnode01{0:02}'.format(i) for i in range(1, self.num_nodes)]
        self.bench_node_list = os.path.join(self.directory, 'node_list')
        bench.util.write_node_list(os.path.join(self.directory, 'node_list'),
                                   self.nodes)
        bench.util.write_node_list(os.path.join(self.node_dir, 'node_list'),
                                   self.nodes)

    def tearDown (self):
        shutil.rmtree(self.directory)

    def test_write_result_files(self):
        '''Test that pass, fail, and error nodes are written to files'''
        self.pass_node_range = [1, 6]
        self.fail_node_range = [self.pass_node_range[1], 9]
        self.error_node_range = [self.fail_node_range[1], self.num_nodes]
        self.pass_nodes = ['tnode01{0:02}'.format(i) for i in range(self.pass_node_range[0], self.pass_node_range[1])]
        self.fail_nodes = ['tnode01{0:02}'.format(i) for i in range(self.fail_node_range[0], self.fail_node_range[1])]
        self.error_nodes = ['tnode01{0:02}'.format(i) for i in range(self.error_node_range[0], self.error_node_range[1])]

        node_test = bench.tests.node_test.NodeTest("node")
        node_test.Process.write_result_files(self.node_dir, self.pass_nodes,
                            self.fail_nodes, self.error_nodes)

        pass_node_string = '\n'.join(self.pass_nodes)
        pass_file = open(os.path.join(self.node_dir, 'pass_nodes')).read()
        self.assertIn(pass_node_string, pass_file)

        fail_node_string = '\n'.join(self.fail_nodes)
        fail_file = open(os.path.join(self.node_dir, 'fail_nodes')).read()
        self.assertIn(fail_node_string, fail_file)

        error_node_string = '\n'.join(self.error_nodes)
        error_file = open(os.path.join(self.node_dir, 'error_nodes')).read()
        self.assertIn(error_node_string, error_file)






















#
